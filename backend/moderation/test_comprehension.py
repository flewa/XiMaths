from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

from django.core.exceptions import PermissionDenied
from django.test import override_settings
from django.utils import timezone

from config import llm
from config.errors import RuleError
from content.models import Review, Solution
from content.services import submit_review
from content.tests import TL, ContentTestCase, make_user
from gamification.models import PointTransaction
from notifications.models import Notification

from . import comprehension
from .models import ComprehensionQuestion
from .services import answer_question, comprehension_tick, evaluate_question, open_question

Status = ComprehensionQuestion.Status
Reason = PointTransaction.Reason
WRITTEN = {"question": "À l'étape 2, pourquoi peut-on comparer à une intégrale ?", "expected_points": ["décroissance"]}


def score(value):
    return mock.patch.object(comprehension, "integrity_score", return_value=value)


class ComprehensionTestCase(ContentTestCase):
    def setUp(self):
        super().setUp()
        make_user("relecteur3", trust=TL.REVIEWER)  # un relecteur de plus, pour la relecture supplémentaire
        self.hard = self.make_exercise(difficulty=5)  # 15 × 2,5 = 38 points : fort enjeu
        self.expert = make_user("experte", trust=TL.EXPERT)

    def publish_hard(self, value):
        with score(value):
            return self.publish(exercise=self.hard)

    def validate(self, solution):
        for review in solution.reviews.filter(submitted_at=None):
            submit_review(review, Review.Verdict.CORRECT)
        solution.refresh_from_db()
        return solution

    def question_sent(self):
        solution = self.publish_hard(0.8)
        question = solution.comprehension_question
        question.question = WRITTEN["question"]
        comprehension.send(question)
        return solution, question


class ThresholdTests(ComprehensionTestCase):
    def test_low_stakes_solutions_are_not_scored(self):
        with score(1.0):
            solution = self.publish()
        self.assertEqual(solution.reviews.count(), 3)
        self.assertFalse(ComprehensionQuestion.objects.exists())

    def test_a_middle_score_adds_a_reviewer(self):
        solution = self.publish_hard(0.5)
        self.assertEqual(solution.reviews.count(), 4)
        self.assertFalse(ComprehensionQuestion.objects.exists())

    def test_a_high_score_asks_a_question_and_holds_the_points(self):
        solution = self.publish_hard(0.8)
        self.assertEqual(solution.comprehension_question.status, Status.TO_WRITE)

        self.validate(solution)
        self.assertEqual(solution.status, Solution.Status.VALIDATED)
        self.assertFalse(PointTransaction.objects.filter(user=self.student, reason=Reason.SOLUTION_VALIDATED).exists())

    def test_one_question_per_fourteen_days(self):
        self.publish_hard(0.8)
        second = self.publish_hard(0.8)
        self.assertFalse(hasattr(second, "comprehension_question") and second.comprehension_question.pk)
        self.assertEqual(second.reviews.count(), 4)

    def test_pasting_into_a_timed_session_raises_the_score(self):
        solution = Solution.objects.create(exercise=self.hard, author=self.student, body="x" * 100)
        session = SimpleNamespace(external_paste_chars=100, exercise=self.hard, pk=None, elapsed_s=600)
        measured = comprehension.signals(solution, session)
        self.assertEqual(measured["collage_temps"], 1.0)
        self.assertGreater(comprehension.integrity_score(solution, session), 0.4)


class FlowTests(ComprehensionTestCase):
    def test_without_a_llm_an_unwritten_question_is_dropped_and_points_released(self):
        solution = self.validate(self.publish_hard(0.8))

        comprehension_tick(now=timezone.now() + timedelta(hours=73))

        self.assertEqual(ComprehensionQuestion.objects.get().status, Status.DROPPED)
        self.assertTrue(PointTransaction.objects.filter(user=self.student, reason=Reason.SOLUTION_VALIDATED).exists())
        self.assertEqual(solution.status, Solution.Status.VALIDATED)

    @override_settings(ANTHROPIC_API_KEY="test")
    def test_with_a_llm_the_question_is_written_sent_and_preassessed(self):
        self.publish_hard(0.8)
        with mock.patch.object(llm, "ask_json", return_value=WRITTEN):
            comprehension_tick()
        question = ComprehensionQuestion.objects.get()
        self.assertEqual((question.status, question.generated_by_llm), (Status.SENT, True))
        self.assertTrue(Notification.objects.filter(user=self.student, kind=Notification.Kind.COMPREHENSION_QUESTION).exists())

        open_question(question, self.student)
        answer_question(question, self.student, "La fonction est décroissante, on compare somme et intégrale.")
        with mock.patch.object(llm, "ask_json", return_value={"assessment": "convaincante", "rationale": "Juste."}):
            comprehension_tick()
        question.refresh_from_db()
        self.assertEqual(question.llm_assessment, "convaincante")

    def test_five_minutes_to_answer(self):
        _, question = self.question_sent()
        opened = timezone.now()
        open_question(question, self.student, now=opened)
        with self.assertRaises(RuleError):
            answer_question(question, self.student, "Trop tard.", now=opened + timedelta(minutes=6))
        comprehension_tick(now=opened + timedelta(minutes=6))
        question.refresh_from_db()
        self.assertEqual(question.status, Status.EXPIRED)

    def test_a_passed_question_releases_the_points_and_a_failed_one_does_not(self):
        solution, question = self.question_sent()
        self.validate(solution)
        open_question(question, self.student)
        answer_question(question, self.student, "Par comparaison série-intégrale.")

        with self.assertRaises(PermissionDenied):
            evaluate_question(question, passed=True, evaluator=self.reviewers[0])
        evaluate_question(question, passed=True, evaluator=self.expert, note="Clair.")

        self.assertTrue(PointTransaction.objects.filter(user=self.student, reason=Reason.SOLUTION_VALIDATED).exists())

    def test_a_failed_question_keeps_the_solution_without_points(self):
        solution, question = self.question_sent()
        self.validate(solution)
        open_question(question, self.student)
        answer_question(question, self.student, "Je ne sais plus.")
        evaluate_question(question, passed=False, evaluator=self.expert)

        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.VALIDATED)
        self.assertFalse(PointTransaction.objects.filter(user=self.student, reason=Reason.SOLUTION_VALIDATED).exists())


class QuestionApiTests(ComprehensionTestCase):
    def test_the_question_is_shown_once_opened_and_evaluated_by_an_expert(self):
        _, question = self.question_sent()
        self.client.force_login(self.student)

        [listed] = self.client.get("/api/questions/mine").json()
        self.assertIsNone(listed["question"])
        opened = self.client.post(f"/api/questions/{question.pk}/open").json()
        self.assertEqual(opened["question"], WRITTEN["question"])
        self.assertIsNotNone(opened["answer_until"])
        answered = self.client.post(
            f"/api/questions/{question.pk}/answer", {"answer": "Décroissance."}, content_type="application/json"
        )
        self.assertEqual(answered.json()["status"], Status.ANSWERED)
        self.assertEqual(self.client.get("/api/questions/to-evaluate").status_code, 403)

        self.client.force_login(self.expert)
        [pending] = self.client.get("/api/questions/to-evaluate").json()
        self.assertEqual(pending["answer"], "Décroissance.")
        response = self.client.post(
            f"/api/questions/{question.pk}/evaluate", {"passed": True}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)
