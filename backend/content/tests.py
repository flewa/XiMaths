import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.utils import timezone

from catalog.models import Level
from gamification.services import balance

from .models import Exercise, Review, Solution
from .services import (
    cast_vote,
    eligible_reviewers,
    publish_exercise,
    publish_solution,
    resolve_contested,
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
        solution = Solution.objects.create(
            exercise=exercise or self.exercise,
            author=author or self.student,
            body="Comparaison avec $1/(n(n-1))$.",
            ai_usage=ai_usage,
        )
        return publish_solution(solution, rng=random.Random(0))

    def review(self, solution, reviewer, verdict):
        review = Review.objects.get(solution=solution, reviewer=reviewer)
        status = submit_review(review, verdict)
        solution.refresh_from_db()
        return status


class PublicationTests(ContentTestCase):
    def test_publishing_an_exercise_pays_five_points(self):
        self.assertEqual(self.exercise.status, Exercise.Status.PUBLISHED)
        self.assertEqual(balance(self.author), 5)

    def test_publishing_a_solution_pays_the_attempt_and_draws_three_reviewers(self):
        solution = self.publish()
        self.assertEqual(solution.status, Solution.Status.UNDER_REVIEW)
        self.assertEqual(balance(self.student), 2)
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
    def test_two_correct_reviews_validate_and_pay_everyone(self):
        solution = self.publish()
        self.review(solution, self.reviewers[0], Verdict.CORRECT)
        status = self.review(solution, self.reviewers[1], Verdict.CORRECT)

        self.assertEqual(status, Solution.Status.VALIDATED)
        # tentative 2 + validée 15 × 1,5 = 23 + première validée 10
        self.assertEqual(balance(self.student), 35)
        # publication 5 + solution validée reçue 3
        self.assertEqual(balance(self.author), 8)
        self.assertEqual(balance(self.reviewers[0]), 2)
        self.assertEqual(balance(self.reviewers[2]), 0)

    def test_second_validated_solution_gets_no_first_bonus(self):
        first = self.publish()
        self.review(first, self.reviewers[0], Verdict.CORRECT)
        self.review(first, self.reviewers[1], Verdict.CORRECT)
        other = make_user("yanis", level="L1")
        second = self.publish(author=other)
        self.review(second, self.reviewers[0], Verdict.CORRECT)
        self.review(second, self.reviewers[1], Verdict.CORRECT)
        self.assertEqual(balance(other), 2 + 23)

    def test_disagreement_is_contested_until_an_expert_decides(self):
        solution = self.publish()
        self.review(solution, self.reviewers[0], Verdict.CORRECT)
        status = self.review(solution, self.reviewers[1], Verdict.INCORRECT)
        self.assertEqual(status, Solution.Status.CONTESTED)

        with self.assertRaises(PermissionDenied):
            resolve_contested(solution, self.reviewers[2], validate=True)

        expert = make_user("expert", trust=TL.EXPERT)
        self.assertEqual(
            resolve_contested(solution, expert, validate=True), Solution.Status.VALIDATED
        )
        self.assertEqual(balance(self.reviewers[0]), 2)
        self.assertEqual(balance(self.reviewers[1]), 0)

    def test_reviews_with_gaps_only_ask_for_more_work(self):
        solution = self.publish()
        for reviewer in self.reviewers:
            status = self.review(solution, reviewer, Verdict.GAPS)
        self.assertEqual(status, Solution.Status.NEEDS_WORK)
        # L'effort reste payé, la validation non.
        self.assertEqual(balance(self.student), 2)
        self.assertEqual(balance(self.reviewers[0]), 2)

    def test_two_incorrect_reviews_close_the_solution(self):
        solution = self.publish()
        self.review(solution, self.reviewers[0], Verdict.INCORRECT)
        status = self.review(solution, self.reviewers[1], Verdict.INCORRECT)
        self.assertEqual(status, Solution.Status.NEEDS_WORK)

    def test_a_verified_teacher_validates_alone(self):
        solution = self.publish()
        teacher = make_user("prof", verified_teacher=True)
        review = Review.objects.create(solution=solution, reviewer=teacher, assigned=True)
        self.assertEqual(submit_review(review, Verdict.CORRECT), Solution.Status.VALIDATED)

    def test_generated_solution_is_validated_without_points(self):
        solution = self.publish(ai_usage=Solution.AiUsage.GENERATED)
        self.review(solution, self.reviewers[0], Verdict.CORRECT)
        self.review(solution, self.reviewers[1], Verdict.CORRECT)
        self.assertEqual(solution.status, Solution.Status.VALIDATED)
        self.assertEqual(balance(self.student), 2)
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
    def test_exercise_list_counts_only_validated_solutions(self):
        validated = self.publish()
        self.review(validated, self.reviewers[0], Verdict.CORRECT)
        self.review(validated, self.reviewers[1], Verdict.CORRECT)
        self.publish(author=make_user("yanis", level="L1"))

        response = self.client.get("/api/exercises", {"level": "L1"})

        self.assertEqual(response.status_code, 200)
        [item] = response.json()
        self.assertEqual(item["validated_solutions"], 1)
        self.assertEqual(item["primary_level"], "L1")

    def test_exercise_detail_hides_drafts_and_unvalidated_solutions(self):
        self.publish()
        draft = Exercise.objects.create(
            author=self.author,
            title="Brouillon",
            statement="…",
            difficulty_declared=1,
            primary_level=Level.objects.get(code="L1"),
        )

        detail = self.client.get(f"/api/exercises/{self.exercise.pk}").json()

        self.assertEqual(detail["solutions"], [])
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
        url = f"/api/exercises/{self.exercise.pk}/solutions"
        body = {"body": "Par comparaison avec une série télescopique, la série converge."}
        response = self.post(url, body, user=self.student)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "under_review")
        self.assertEqual(self.post(url, body).status_code, 409)

        self.client.force_login(self.reviewers[0])
        [task] = self.client.get("/api/reviews").json()
        self.assertNotIn("author", task)  # relecture anonyme
        self.post(f"/api/reviews/{task['id']}", {"verdict": "correcte", "feedback": "Clair."})
        self.client.force_login(self.reviewers[1])
        [task] = self.client.get("/api/reviews").json()
        result = self.post(f"/api/reviews/{task['id']}", {"verdict": "correcte"})
        self.assertEqual(result.json(), {"solution_status": "validated"})

        self.client.force_login(self.student)
        [mine] = self.client.get(f"/api/exercises/{self.exercise.pk}/my-solutions").json()
        self.assertEqual(mine["status"], "validated")
        self.assertEqual(mine["feedback"], ["Clair."])

    def test_a_negative_verdict_needs_an_explanation(self):
        review = self.publish().reviews.first()
        url = f"/api/reviews/{review.pk}"
        self.client.force_login(review.reviewer)
        self.assertEqual(self.post(url, {"verdict": "lacunes"}).status_code, 422)
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

    def test_a_solution_upvote_pays_two_points(self):
        solution = self.publish()
        cast_vote(self.author, solution=solution)
        self.assertEqual(balance(self.student), 2 + 2)

    def test_nobody_votes_for_themselves(self):
        with self.assertRaises(PermissionDenied):
            cast_vote(self.author, exercise=self.exercise)
