from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone

from config.errors import RuleError
from content.models import Exercise, Solution
from content.tests import ContentTestCase, make_user

from .answers import check_answer
from .models import TimedSession
from .services import (
    abandon,
    median_elapsed_s,
    pause,
    rate,
    remaining_s,
    resume,
    save,
    start,
    submit,
)

Status = TimedSession.Status
PROOF = "Par le critère de d'Alembert, le rayon vaut 2 : le quotient tend vers |x|/2."


class AnswerTests(SimpleTestCase):
    def test_equivalent_answers_are_accepted(self):
        for given, expected in [
            ("2", "2"),
            ("R = 2", "2"),
            ("4/2", "R = 2"),
            ("√2/2", "1/sqrt(2)"),
            ("π/4", "pi/4"),
            ("1,5", "3/2"),
            ("e^2", "exp(2)"),
            ("2x", "x*2"),
            ("oo", "+infty"),
        ]:
            with self.subTest(given=given):
                self.assertIs(check_answer(given, expected), True)

    def test_wrong_and_unreadable_answers(self):
        self.assertIs(check_answer("3", "2"), False)
        self.assertIsNone(check_answer("2", ""))
        self.assertIsNone(check_answer("deux", "2"))

    def test_hostile_inputs_never_reach_python(self):
        for given in ["__import__('os')", "x.func", "().__class__", "2**1000**1000", "9^9^9", "x" * 101]:
            with self.subTest(given=given):
                self.assertIsNone(check_answer(given, "2"))


class SessionTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.t0 = timezone.now()
        Exercise.objects.filter(pk=self.exercise.pk).update(final_answer="R = 2")
        self.exercise.refresh_from_db()

    def at(self, seconds):
        return self.t0 + timedelta(seconds=seconds)

    def session(self, minutes=15, user=None):
        return start(user or self.student, self.exercise, minutes=minutes, now=self.t0)

    def test_starting_twice_resumes_the_open_session(self):
        first = self.session()
        self.assertEqual(self.session(minutes=30).pk, first.pk)
        with self.assertRaises(RuleError):
            start(make_user("autre"), self.exercise, minutes=20, now=self.t0)

    def test_extra_time_applies_to_the_limit(self):
        session = self.session(user=make_user("tiers", tiers_temps=True))
        self.assertAlmostEqual(session.limit_s, 15 * 60 * 1.33)

    def test_a_pending_solution_blocks_training_on_the_same_exercise(self):
        self.publish()
        with self.assertRaises(RuleError):
            self.session()

    def test_the_clock_only_runs_while_the_browser_is_there(self):
        session = self.session()
        save(session, draft="a", now=self.at(10))
        save(session, draft="ab", now=self.at(20))
        # Onglet fermé deux minutes : ce temps ne compte pas.
        save(session, draft="abc", now=self.at(140))
        save(session, draft="abcd", now=self.at(150))
        self.assertAlmostEqual(session.elapsed_s, 30)
        self.assertAlmostEqual(remaining_s(session, now=self.at(155)), 15 * 60 - 35)

    def test_two_pauses_then_no_more(self):
        session = self.session()
        pause(session, now=self.at(10))
        self.assertAlmostEqual(remaining_s(session, now=self.at(500)), 15 * 60 - 10)
        resume(session, now=self.at(500))
        pause(session, now=self.at(505))
        resume(session, now=self.at(600))
        with self.assertRaises(RuleError):
            pause(session, now=self.at(601))
        self.assertAlmostEqual(session.elapsed_s, 15)

    def run_to_the_deadline(self, session):
        for second in range(10, 15 * 60 + 1, 10):
            save(session, draft="brouillon", now=self.at(second))

    def test_a_save_within_the_grace_period_is_the_final_version(self):
        session = self.session()
        self.run_to_the_deadline(session)
        session.refresh_from_db()
        self.assertEqual(session.status, Status.RUNNING)

        save(session, draft=PROOF, final_answer="2", now=self.at(15 * 60 + 20))

        self.assertEqual(session.status, Status.SUBMITTED)
        self.assertEqual((session.draft, session.answer_correct), (PROOF, True))
        self.assertAlmostEqual(session.elapsed_s, 15 * 60)

    def test_a_save_after_the_grace_period_keeps_the_last_version(self):
        session = self.session()
        save(session, draft=PROOF, now=self.at(10))
        # Au-delà de 30 s sans signe de vie, le chrono s'arrête : on simule 15 min actives.
        TimedSession.objects.filter(pk=session.pk).update(elapsed_s=15 * 60 + 70)
        session.refresh_from_db()

        save(session, draft="trop tard", now=self.at(20))

        self.assertEqual((session.status, session.draft), (Status.SUBMITTED, PROOF))

    def test_submitting_checks_the_answer_and_sends_the_proof_to_review(self):
        session = self.session()
        submit(session, draft=PROOF, final_answer="R = 4/2", ai_usage="relecture", now=self.at(300))

        self.assertEqual((session.status, session.answer_correct), (Status.SUBMITTED, True))
        solution = session.solution
        self.assertEqual(
            (solution.origin, solution.status, solution.ai_usage),
            (Solution.Origin.TRAINING, Solution.Status.UNDER_REVIEW, "relecture"),
        )
        with self.assertRaises(RuleError):
            save(session, draft="encore", now=self.at(310))

    def test_a_short_draft_is_not_sent_to_review(self):
        session = self.session()
        submit(session, draft="Rayon : 2", final_answer="3", now=self.at(60))
        self.assertIsNone(session.solution)
        self.assertIs(session.answer_correct, False)

    def test_abandoning_ends_the_session(self):
        session = self.session()
        abandon(session, now=self.at(30))
        self.assertEqual(session.status, Status.ABANDONED)
        self.assertNotEqual(self.session().pk, session.pk)

    def test_self_rating_refines_the_estimated_difficulty(self):
        for name, rating in [("a", 2), ("b", 4)]:
            session = self.session(user=make_user(name))
            submit(session, draft="", now=self.at(60))
            rate(session, rating)
        self.exercise.refresh_from_db()
        self.assertEqual((self.exercise.difficulty_estimated, self.exercise.difficulty_ratings), (3, 2))
        with self.assertRaises(RuleError):
            rate(session, 5)

    def test_median_time_of_other_sessions(self):
        for name, seconds in [("a", 100), ("b", 300), ("c", 200)]:
            session = self.session(user=make_user(name))
            for second in range(10, seconds + 1, 10):
                save(session, draft="", now=self.at(second))
            submit(session, draft="", now=self.at(seconds))
        self.assertEqual(median_elapsed_s(self.exercise), 200)
        self.assertEqual(median_elapsed_s(self.exercise, exclude=session), 200)


class TrainingApiTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.student.email_verified_at = timezone.now()
        self.student.save()
        self.client.force_login(self.student)

    def post(self, url, data=None):
        return self.client.post(url, data or {}, content_type="application/json")

    def test_a_full_session_through_the_api(self):
        options = self.client.get(f"/api/training/options/{self.exercise.pk}").json()
        self.assertEqual(options["recommended"], 45)  # difficulté 3

        session = self.post("/api/training/sessions", {"exercise_id": self.exercise.pk, "minutes": 15}).json()
        self.assertEqual((session["status"], session["pauses_left"]), ("en_cours", 2))
        self.assertLessEqual(session["remaining_s"], 15 * 60)
        url = f"/api/training/sessions/{session['id']}"

        saved = self.post(f"{url}/save", {"draft": "début", "focus_losses": 1}).json()
        self.assertEqual((saved["draft"], saved["focus_losses"]), ("début", 1))
        self.assertEqual(self.post(f"{url}/pause").json()["status"], "en_pause")
        self.assertEqual(self.post(f"{url}/resume").json()["status"], "en_cours")

        done = self.post(f"{url}/submit", {"draft": PROOF, "final_answer": "2"}).json()
        self.assertEqual((done["status"], done["solution_status"]), ("rendue", "under_review"))
        self.assertEqual(self.post(f"{url}/rating", {"rating": 3}).json()["self_rating"], 3)

        self.client.force_login(make_user("curieux"))
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_bad_durations_are_refused(self):
        response = self.post("/api/training/sessions", {"exercise_id": self.exercise.pk, "minutes": 7})
        self.assertEqual(response.status_code, 409)

    def test_extra_time_is_declared_in_preferences(self):
        response = self.post("/api/auth/preferences", {"tiers_temps": True})
        self.assertTrue(response.json()["tiers_temps"])
        options = self.client.get(f"/api/training/options/{self.exercise.pk}").json()
        self.assertEqual(options["extra_time_factor"], 1.33)
