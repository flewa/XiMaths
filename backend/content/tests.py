import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.utils import timezone

from config.errors import RuleError
from catalog.models import Level, Topic
from gamification.services import balance

from .models import Exercise, Review, Solution
from .services import (
    cast_vote,
    eligible_reviewers,
    publish_exercise,
    publish_solution,
    resolve_contested,
    review_deadlines,
    submit_review,
)

User = get_user_model()
TL = User.TrustLevel
Verdict = Review.Verdict


def make_user(name, *, trust=TL.MEMBER, level="L2", joined_days_ago=30, **fields):
    return User.objects.create_user(
        name,
        f"{name}@example.com",
        trust_level=trust,
        declared_level=Level.objects.get(code=level) if level else None,
        date_joined=timezone.now() - timedelta(days=joined_days_ago),
        **fields,
    )


class ContentTestCase(TestCase):
    def setUp(self):
        self.author = make_user("auteur")
        self.student = make_user("lea", level="L1")
        self.reviewers = [make_user(f"relecteur{i}", trust=TL.REVIEWER) for i in range(3)]
        self.exercise = self.make_exercise()

    def make_exercise(self, *, level="L1", difficulty=3, author=None):
        exercise = Exercise.objects.create(
            author=author or self.author,
            title="Série de Riemann",
            statement="Étudier la convergence de $\\sum 1/n^2$.",
            difficulty_declared=difficulty,
            primary_level=Level.objects.get(code=level),
        )
        return publish_exercise(exercise)

    def publish(self, *, author=None, ai_usage=Solution.AiUsage.NONE, exercise=None):
        author = author or self.student
        # Un texte propre à chaque auteur : deux copies identiques seraient mises en vérification.
        solution = Solution.objects.create(
            exercise=exercise or self.exercise,
            author=author,
            body=f"Preuve de {author.username} : on compare avec $1/(n(n-1))$, selon {author.username}.",
            ai_usage=ai_usage,
        )
        return publish_solution(solution, rng=random.Random(0))

    def review(self, solution, reviewer, verdict):
        review = Review.objects.get(solution=solution, reviewer=reviewer, round=solution.review_round)
        status = submit_review(review, verdict, feedback="Commentaire du relecteur.")
        solution.refresh_from_db()
        return status

    def validate(self, solution):
        """Les trois relecteurs tirés au sort jugent la copie correcte : le consensus."""
        status = None
        for review in solution.reviews.filter(round=solution.review_round, assigned=True, expired_at=None):
            status = self.review(solution, review.reviewer, Verdict.CORRECT)
        return status


class PublicationTests(ContentTestCase):
    def test_publishing_an_exercise_pays_five_points(self):
        self.assertEqual(self.exercise.status, Exercise.Status.PUBLISHED)
        self.assertEqual(balance(self.author), 5)

    def test_publishing_a_solution_pays_nothing_and_draws_three_reviewers(self):
        solution = self.publish()
        self.assertEqual(solution.status, Solution.Status.UNDER_REVIEW)
        # Les points ne viennent qu'avec le consensus des relecteurs.
        self.assertEqual(balance(self.student), 0)
        reviewers = set(solution.reviews.values_list("reviewer_id", flat=True))
        self.assertEqual(reviewers, {r.pk for r in self.reviewers})

    def test_reviewers_need_trust_and_a_high_enough_level(self):
        exercise = self.make_exercise(level="L2")
        newcomer = make_user("nouveau", trust=TL.MEMBER)
        first_year = make_user("premiere-annee", trust=TL.REVIEWER, level="L1")
        teacher = make_user("prof", trust=TL.NEW, level=None, verified_teacher=True)
        solution = Solution.objects.create(exercise=exercise, author=self.reviewers[0], body="…")

        eligible = set(eligible_reviewers(solution))

        self.assertNotIn(newcomer, eligible)
        self.assertNotIn(first_year, eligible)
        self.assertNotIn(self.reviewers[0], eligible)  # l'auteur
        self.assertIn(teacher, eligible)
        self.assertIn(self.reviewers[1], eligible)


class ReviewQuorumTests(ContentTestCase):
    def test_three_correct_reviews_validate_and_pay_everyone(self):
        solution = self.publish()
        self.review(solution, self.reviewers[0], Verdict.CORRECT)
        status = self.review(solution, self.reviewers[1], Verdict.CORRECT)
        # Deux avis ne suffisent pas : on attend le troisième.
        self.assertEqual(status, Solution.Status.UNDER_REVIEW)
        self.assertEqual(balance(self.student), 0)
        status = self.review(solution, self.reviewers[2], Verdict.CORRECT)

        self.assertEqual(status, Solution.Status.VALIDATED)
        # validée 15 × 1,5 = 23 + première validée 10
        self.assertEqual(balance(self.student), 33)
        # publication 5 + solution validée reçue 3
        self.assertEqual(balance(self.author), 8)
        self.assertEqual([balance(reviewer) for reviewer in self.reviewers], [2, 2, 2])

    def test_correct_with_gaps_still_counts_for_the_consensus(self):
        solution = self.publish()
        self.review(solution, self.reviewers[0], Verdict.CORRECT)
        self.review(solution, self.reviewers[1], Verdict.GAPS)
        self.assertEqual(self.review(solution, self.reviewers[2], Verdict.CORRECT), Solution.Status.VALIDATED)

    def test_second_validated_solution_gets_no_first_bonus(self):
        self.validate(self.publish())
        other = make_user("yanis", level="L1")
        self.validate(self.publish(author=other))
        self.assertEqual(balance(other), 23)

    def test_without_consensus_the_copy_is_to_rework_and_pays_nothing(self):
        solution = self.publish()
        self.review(solution, self.reviewers[0], Verdict.CORRECT)
        self.review(solution, self.reviewers[1], Verdict.CORRECT)
        status = self.review(solution, self.reviewers[2], Verdict.INCORRECT)

        self.assertEqual(status, Solution.Status.NEEDS_WORK)
        self.assertEqual(balance(self.student), 0)
        # Les relecteurs de la majorité sont rémunérés, pas le troisième.
        self.assertEqual([balance(reviewer) for reviewer in self.reviewers], [2, 2, 0])

    def test_a_majority_of_incorrect_reviews_pays_those_reviewers(self):
        solution = self.publish()
        self.review(solution, self.reviewers[0], Verdict.INCORRECT)
        self.review(solution, self.reviewers[1], Verdict.GAPS)
        status = self.review(solution, self.reviewers[2], Verdict.INCORRECT)
        self.assertEqual(status, Solution.Status.NEEDS_WORK)
        self.assertEqual([balance(reviewer) for reviewer in self.reviewers], [2, 0, 2])

    def test_an_expert_still_decides_a_solution_contested_under_the_former_rule(self):
        solution = self.publish()
        Solution.objects.filter(pk=solution.pk).update(status=Solution.Status.CONTESTED)
        solution.refresh_from_db()
        with self.assertRaises(PermissionDenied):
            resolve_contested(solution, self.reviewers[2], validate=True)
        expert = make_user("expert", trust=TL.EXPERT)
        self.assertEqual(resolve_contested(solution, expert, validate=True), Solution.Status.VALIDATED)

    def test_a_verified_teacher_counts_as_one_reviewer(self):
        solution = self.publish()
        teacher = make_user("prof", verified_teacher=True)
        review = Review.objects.create(solution=solution, reviewer=teacher, assigned=True)
        self.assertEqual(submit_review(review, Verdict.CORRECT), Solution.Status.UNDER_REVIEW)

    def test_a_short_draw_is_completed_when_reviewers_appear(self):
        lone = Solution.objects.create(exercise=self.exercise, author=self.student, body="Ma preuve, seule.")
        Review.objects.filter(solution=lone).delete()
        for reviewer in self.reviewers[1:]:
            reviewer.is_active = False
            reviewer.save()
        publish_solution(lone, rng=random.Random(0))
        self.assertEqual(lone.reviews.count(), 1)
        for reviewer in self.reviewers[1:]:
            reviewer.is_active = True
            reviewer.save()
        review_deadlines()
        self.assertEqual(lone.reviews.filter(assigned=True, expired_at=None).count(), 3)

    def test_generated_solution_is_validated_without_points(self):
        solution = self.publish(ai_usage=Solution.AiUsage.GENERATED)
        self.validate(solution)
        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.VALIDATED)
        self.assertEqual(balance(self.student), 0)
        self.assertEqual(balance(self.author), 5)

    def test_nobody_reviews_their_own_solution(self):
        solution = self.publish(author=self.reviewers[0])
        own = Review.objects.create(solution=solution, reviewer=self.reviewers[0])
        with self.assertRaises(PermissionDenied):
            submit_review(own, Verdict.CORRECT)

    def test_a_review_counts_once(self):
        solution = self.publish()
        review = Review.objects.get(solution=solution, reviewer=self.reviewers[0])
        submit_review(review, Verdict.CORRECT)
        with self.assertRaises(ValueError):
            submit_review(review, Verdict.CORRECT)


class ApiTests(ContentTestCase):
    def test_exercise_list_counts_the_solutions_sent(self):
        self.validate(self.publish())
        self.publish(author=make_user("yanis", level="L1"))

        response = self.client.get("/api/exercises", {"level": "L1"})

        self.assertEqual(response.status_code, 200)
        [item] = response.json()
        self.assertEqual((item["validated_solutions"], item["submitted_solutions"]), (1, 2))
        self.assertEqual(item["primary_level"], "L1")
        self.assertEqual(self.client.get("/api/exercises", {"sort": "unsolved"}).json(), [])

    def test_exercise_list_filters_by_chapter(self):
        algebra = self.make_exercise()
        algebra.topics.set(Topic.objects.filter(slug="algebre"))

        response = self.client.get("/api/exercises", {"topic": "algebre"})

        self.assertEqual([item["id"] for item in response.json()], [algebra.pk])

    def test_exercise_detail_shows_no_solution_and_hides_drafts(self):
        self.validate(self.publish())
        draft = Exercise.objects.create(
            author=self.author,
            title="Brouillon",
            statement="…",
            difficulty_declared=1,
            primary_level=Level.objects.get(code="L1"),
        )

        detail = self.client.get(f"/api/exercises/{self.exercise.pk}").json()

        self.assertNotIn("solutions", detail)
        self.assertEqual(detail["submitted_solutions"], 1)
        self.assertEqual(self.client.get(f"/api/exercises/{draft.pk}").status_code, 404)


class WriteApiTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        User.objects.update(email_verified_at=timezone.now())
        for user in (self.author, self.student, *self.reviewers):
            user.refresh_from_db()

    def post(self, url, data=None, *, user=None):
        if user is not None:
            self.client.force_login(user)
        return self.client.post(url, data or {}, content_type="application/json")

    def exercise_payload(self, **fields):
        return {
            "title": "Nilpotence",
            "statement": "Soit $A$ nilpotente. Montrer que $I - A$ est inversible.",
            "difficulty": 2,
            "primary_level": "L2",
            "levels": ["MP"],
            "topics": ["algebre-lineaire"],
            "hints": ["Penser à une série géométrique.", "  "],
            **fields,
        }

    def test_anonymous_writes_are_refused(self):
        self.assertEqual(self.post("/api/exercises", self.exercise_payload()).status_code, 401)

    def test_an_unverified_account_cannot_contribute(self):
        response = self.post("/api/exercises", self.exercise_payload(), user=make_user("nouveau"))
        self.assertEqual(response.status_code, 403)
        self.assertIn("Vérifie", response.json()["detail"])

    def test_create_then_publish_an_exercise(self):
        draft = self.post("/api/exercises", self.exercise_payload(), user=self.author)
        self.assertEqual(draft.status_code, 201)
        exercise_id = draft.json()["id"]
        # Un brouillon n'est pas visible.
        self.assertEqual(self.client.get(f"/api/exercises/{exercise_id}").status_code, 404)

        published = self.post(f"/api/exercises/{exercise_id}/publish")

        self.assertEqual(published.status_code, 200)
        self.assertEqual(sorted(published.json()["levels"]), ["L2", "MP"])
        self.assertEqual(published.json()["hints"], ["Penser à une série géométrique."])
        self.assertEqual(self.post(f"/api/exercises/{exercise_id}/publish").status_code, 409)

    def test_only_the_author_publishes_a_draft(self):
        draft = self.post("/api/exercises", self.exercise_payload(), user=self.author).json()
        response = self.post(f"/api/exercises/{draft['id']}/publish", user=self.student)
        self.assertEqual(response.status_code, 404)

    def test_macro_definitions_are_refused(self):
        payload = self.exercise_payload(statement="$\\def\\x{1}$ Montrer que $\\x = 1$.")
        response = self.post("/api/exercises", payload, user=self.author)
        self.assertEqual(response.status_code, 422)
        self.assertIn("\\def", response.json()["detail"])

    def test_an_unknown_level_or_a_missing_source_is_refused(self):
        for fields in ({"primary_level": "X9"}, {"source_type": "inspire"}):
            with self.subTest(**fields):
                response = self.post("/api/exercises", self.exercise_payload(**fields), user=self.author)
                self.assertEqual(response.status_code, 422)

    def test_propose_a_solution_then_review_it(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from .test_photos import MEDIA, jpeg

        url = f"/api/exercises/{self.exercise.pk}/solutions"
        with self.settings(MEDIA_ROOT=MEDIA):
            token = self.post(f"/api/exercises/{self.exercise.pk}/photo-uploads", user=self.student).json()["token"]
            photo = SimpleUploadedFile("copie.jpg", jpeg(), content_type="image/jpeg")
            self.assertEqual(self.client.post(f"/api/photo-uploads/{token}/photos", {"photo": photo}).status_code, 201)
            response = self.post(url, {"photo_upload": token}, user=self.student)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "under_review")
        self.assertEqual(self.post(url, {"photo_upload": token}).status_code, 409)

        self.client.force_login(self.reviewers[0])
        [task] = self.client.get("/api/reviews").json()
        self.assertNotIn("author", task)  # relecture anonyme
        self.post(f"/api/reviews/{task['id']}", {"verdict": "correcte", "feedback": "Clair."})

        # L'auteur lit le premier commentaire aussitôt, et en est prévenu.
        self.client.force_login(self.student)
        [mine] = self.client.get(f"/api/exercises/{self.exercise.pk}/my-solutions").json()
        self.assertEqual(mine["status"], "under_review")
        self.assertEqual(
            [(r["verdict_label"], r["comment"]) for r in mine["reviews"]], [("Correcte", "Clair.")]
        )
        self.assertEqual(mine["reviews_expected"], 3)
        self.assertTrue(self.student.notifications.filter(kind="solution_relue").exists())

        for reviewer, comment in ((self.reviewers[1], "Bien rédigé."), (self.reviewers[2], "Juste.")):
            self.client.force_login(reviewer)
            [task] = self.client.get("/api/reviews").json()
            result = self.post(f"/api/reviews/{task['id']}", {"verdict": "correcte", "feedback": comment})
        self.assertEqual(result.json(), {"solution_status": "validated"})

        self.client.force_login(self.student)
        [mine] = self.client.get(f"/api/exercises/{self.exercise.pk}/my-solutions").json()
        self.assertEqual(mine["status"], "validated")
        self.assertEqual([r["comment"] for r in mine["reviews"]], ["Clair.", "Bien rédigé.", "Juste."])
        # Les autres ne voient ni la solution ni ses photos.
        self.client.force_login(self.author)
        self.assertNotIn("solutions", self.client.get(f"/api/exercises/{self.exercise.pk}").json())

    def test_every_verdict_needs_a_comment_for_the_author(self):
        review = self.publish().reviews.first()
        url = f"/api/reviews/{review.pk}"
        self.client.force_login(review.reviewer)
        self.assertEqual(self.post(url, {"verdict": "lacunes"}).status_code, 422)
        self.assertEqual(self.post(url, {"verdict": "correcte", "feedback": "   "}).status_code, 422)
        response = self.post(url, {"verdict": "lacunes", "feedback": "Justifier la majoration."})
        self.assertEqual(response.status_code, 200)

    def test_nobody_submits_someone_elses_review(self):
        review = self.publish().reviews.first()
        response = self.post(f"/api/reviews/{review.pk}", {"verdict": "correcte"}, user=self.student)
        self.assertEqual(response.status_code, 404)

    def test_votes_are_unique_and_never_for_oneself(self):
        url = f"/api/exercises/{self.exercise.pk}/vote"
        self.assertEqual(self.post(url, user=self.student).status_code, 201)
        self.assertEqual(self.post(url).status_code, 409)
        self.assertEqual(self.post(url, user=self.author).status_code, 403)

    def test_only_validated_solutions_can_be_voted_for(self):
        solution = self.publish()
        response = self.post(f"/api/solutions/{solution.pk}/vote", user=self.author)
        self.assertEqual(response.status_code, 404)


class VoteTests(ContentTestCase):
    def test_repeated_votes_for_the_same_author_lose_weight(self):
        voter = make_user("votant")
        exercises = [self.exercise] + [self.make_exercise() for _ in range(3)]
        weights = [float(cast_vote(voter, exercise=e).weight) for e in exercises]
        self.assertEqual(weights, [1.0, 0.5, 0.25, 0.0])
        # 3 publications payées (plafond quotidien) = 15, puis votes : 1 + 1 + 0 + 0
        self.assertEqual(balance(self.author), 15 + 2)

    def test_votes_from_new_accounts_earn_nothing(self):
        newcomer = make_user("nouveau", joined_days_ago=2)
        vote = cast_vote(newcomer, exercise=self.exercise)
        self.assertEqual(vote.weight, 0)
        self.assertEqual(balance(self.author), 5)

    def test_solutions_are_private_so_nobody_votes_for_them(self):
        solution = self.publish()
        with self.assertRaises(RuleError):
            cast_vote(self.author, solution=solution)
        self.assertEqual(balance(self.student), 0)

    def test_nobody_votes_for_themselves(self):
        with self.assertRaises(PermissionDenied):
            cast_vote(self.author, exercise=self.exercise)


class SitemapTests(ContentTestCase):
    def test_the_sitemap_lists_published_exercises_only(self):
        draft = Exercise.objects.create(
            author=self.author, title="Brouillon", statement="Énoncé.", difficulty_declared=1,
            primary_level=self.exercise.primary_level,
        )
        ids = [entry["id"] for entry in self.client.get("/api/sitemap").json()]
        self.assertIn(self.exercise.pk, ids)
        self.assertNotIn(draft.pk, ids)
