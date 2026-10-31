from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from config.errors import RuleError
from gamification.services import balance
from notifications.models import Notification

from .models import Review, Solution
from .services import recommend_solution, review_deadlines, revise_solution, submit_review, volunteer_review
from .tests import TL, ContentTestCase, make_user

Verdict = Review.Verdict


class ReviewFlowTestCase(ContentTestCase):
    def setUp(self):
        super().setUp()
        # Assez de relecteurs pour une réattribution ou un second tour.
        self.reviewers += [make_user(f"relecteur{i}", trust=TL.REVIEWER) for i in range(3, 7)]

    def assigned(self, solution):
        return list(solution.reviews.filter(round=solution.review_round, expired_at=None).select_related("reviewer"))


class DeadlineTests(ReviewFlowTestCase):
    def test_a_reminder_at_48_hours_then_reassignment_at_72(self):
        solution = self.publish()
        first = self.assigned(solution)[0]
        start = first.assigned_at

        self.assertEqual(review_deadlines(now=start + timedelta(hours=49)), (3, 0))
        self.assertEqual(review_deadlines(now=start + timedelta(hours=50)), (0, 0))
        self.assertTrue(Notification.objects.filter(user=first.reviewer, kind=Notification.Kind.REVIEW_REMINDER).exists())

        self.assertEqual(review_deadlines(now=start + timedelta(hours=73)), (0, 3))
        first.refresh_from_db()
        self.assertIsNotNone(first.expired_at)
        self.assertEqual(len(self.assigned(solution)), 3)
        self.assertNotIn(first.reviewer, [r.reviewer for r in self.assigned(solution)])
        with self.assertRaises(RuleError):
            submit_review(first, Verdict.CORRECT)


class VolunteerTests(ReviewFlowTestCase):
    def test_a_volunteer_review_weighs_half(self):
        solution = self.publish()
        volunteer = self.reviewers[-1]
        if solution.reviews.filter(reviewer=volunteer).exists():
            volunteer = make_user("volontaire", trust=TL.REVIEWER)

        review = volunteer_review(solution, volunteer)
        submit_review(review, Verdict.CORRECT)

        review.refresh_from_db()
        self.assertEqual((review.assigned, review.weight), (False, Decimal("0.5")))
        with self.assertRaises(RuleError):
            volunteer_review(solution, volunteer)

    def test_reviewers_list_the_solutions_open_to_volunteers(self):
        solution = self.publish()
        volunteer = make_user("volontaire", trust=TL.REVIEWER, email_verified_at=timezone.now())
        self.client.force_login(volunteer)

        response = self.client.get("/api/reviews/open")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["solution_id"] for item in response.json()], [solution.pk])

    def test_members_and_the_author_cannot_volunteer(self):
        solution = self.publish()
        with self.assertRaises(PermissionDenied):
            volunteer_review(solution, make_user("membre"))
        with self.assertRaises(PermissionDenied):
            volunteer_review(solution, self.student)


class RevisionTests(ReviewFlowTestCase):
    def needs_work(self):
        solution = self.publish()
        for review in self.assigned(solution):
            submit_review(review, Verdict.INCORRECT, feedback="Étape fausse.")
        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.NEEDS_WORK)
        return solution

    def test_a_revised_solution_gets_a_fresh_round_of_reviewers(self):
        solution = self.needs_work()
        previous = {r.reviewer_id for r in solution.reviews.all()}

        revised, new_round = revise_solution(solution, "Nouvelle preuve, complète cette fois : on compare à une série télescopique.")

        self.assertTrue(new_round)
        self.assertEqual((revised.status, revised.review_round), (Solution.Status.UNDER_REVIEW, 2))
        current = {r.reviewer_id for r in self.assigned(revised)}
        self.assertEqual(len(current), 3)
        self.assertFalse(current & previous)
        for review in self.assigned(revised)[:2]:
            submit_review(review, Verdict.CORRECT)
        revised.refresh_from_db()
        self.assertEqual(revised.status, Solution.Status.VALIDATED)

    def test_a_small_edit_of_a_validated_solution_stays_validated(self):
        solution = self.publish()
        for review in self.assigned(solution)[:2]:
            submit_review(review, Verdict.CORRECT)
        solution.refresh_from_db()

        _, new_round = revise_solution(solution, solution.body + " Fin.")
        self.assertFalse(new_round)
        self.assertEqual(solution.status, Solution.Status.VALIDATED)

        _, new_round = revise_solution(solution, "Une tout autre démarche, par comparaison avec une intégrale de 1/t².")
        self.assertTrue(new_round)
        self.assertEqual(solution.status, Solution.Status.UNDER_REVIEW)

    def test_only_closed_solutions_can_be_revised(self):
        with self.assertRaises(RuleError):
            revise_solution(self.publish(), "Texte assez long pour être une solution valable.")


class RecommendationTests(ReviewFlowTestCase):
    def validated(self, author=None):
        solution = self.publish(author=author)
        for review in self.assigned(solution)[:2]:
            submit_review(review, Verdict.CORRECT)
        solution.refresh_from_db()
        return solution

    def test_the_exercise_author_recommends_one_solution(self):
        solution = self.validated()
        before = balance(self.student)

        recommend_solution(solution, self.author)

        self.assertEqual(balance(self.student), before + 5)
        detail = self.client.get(f"/api/exercises/{self.exercise.pk}").json()
        self.assertTrue(detail["solutions"][0]["recommended"])
        other = self.validated(author=make_user("yanis", level="L1"))
        with self.assertRaises(RuleError):
            recommend_solution(other, self.author)

    def test_only_the_exercise_author_recommends(self):
        with self.assertRaises(PermissionDenied):
            recommend_solution(self.validated(), self.reviewers[0])


class ArbitrationApiTests(ReviewFlowTestCase):
    def contested(self):
        solution = self.publish()
        reviews = self.assigned(solution)
        submit_review(reviews[0], Verdict.CORRECT)
        submit_review(reviews[1], Verdict.INCORRECT, feedback="Faux.")
        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.CONTESTED)
        return solution

    def test_an_expert_sees_the_verdicts_and_decides(self):
        solution = self.contested()
        expert = make_user("experte", trust=TL.EXPERT, email_verified_at=timezone.now())
        self.client.force_login(expert)

        [item] = self.client.get("/api/arbitrations").json()
        self.assertEqual({r["verdict"] for r in item["reviews"]}, {"correcte", "incorrecte"})
        response = self.client.post(
            f"/api/arbitrations/{solution.pk}", {"validate_solution": True}, content_type="application/json"
        )
        self.assertEqual(response.json()["solution_status"], "validated")

    def test_members_cannot_arbitrate(self):
        self.contested()
        self.client.force_login(make_user("membre", trust=TL.MEMBER))
        self.assertEqual(self.client.get("/api/arbitrations").status_code, 403)
