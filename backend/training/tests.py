import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from config.errors import RuleError
from content import photos
from content.models import Exercise, Solution
from content.test_photos import jpeg
from content.tests import ContentTestCase, make_user

from .answers import check_answer
from .models import TimedSession
from .services import (
    abandon,
    median_elapsed_s,
    pause,
    photo_upload,
    rate,
    remaining_s,
    resume,
    save,
    start,
    submit,
)

Status = TimedSession.Status
MEDIA = tempfile.mkdtemp(prefix="ximaths-entrainement-")


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


@override_settings(MEDIA_ROOT=MEDIA)
class SessionTests(ContentTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.t0 = timezone.now()
        Exercise.objects.filter(pk=self.exercise.pk).update(final_answer="R = 2")
        self.exercise.refresh_from_db()

    def at(self, seconds):
        return self.t0 + timedelta(seconds=seconds)

    def session(self, minutes=15, user=None):
        return start(user or self.student, self.exercise, minutes=minutes, now=self.t0)

    def photograph(self, session, seconds):
        """Le téléphone dépose une page de la copie, `seconds` après le départ."""
        return photos.add_photo(photo_upload(session, now=self.at(seconds)), jpeg(), now=self.at(seconds))

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
        save(session, now=self.at(10))
        save(session, now=self.at(20))
        # Onglet fermé deux minutes : ce temps ne compte pas.
        save(session, now=self.at(140))
        save(session, now=self.at(150))
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
            save(session, now=self.at(second))

    def test_the_session_upload_is_the_same_on_every_call(self):
        session = self.session()
        upload = photo_upload(session, now=self.at(5))
        self.assertEqual(photo_upload(session, now=self.at(6)).pk, upload.pk)
        state = photos.upload_state(upload, now=self.at(5))
        self.assertTrue(state["timed"] and state["open"])

    def test_photos_arrive_until_the_deadline_and_the_grace_minute(self):
        session = self.session()
        self.run_to_the_deadline(session)
        session.refresh_from_db()
        self.assertEqual(session.status, Status.RUNNING)

        self.photograph(session, 15 * 60 + 20)
        save(session, now=self.at(15 * 60 + 30))
        save(session, now=self.at(15 * 60 + 40))
        save(session, now=self.at(15 * 60 + 50))
        save(session, now=self.at(15 * 60 + 60))
        save(session, now=self.at(15 * 60 + 70))

        # Grâce écoulée : la session est rendue avec la photo arrivée, et le dépôt est fermé.
        self.assertEqual(session.status, Status.SUBMITTED)
        self.assertEqual(session.solution.photos.count(), 1)
        self.assertAlmostEqual(session.elapsed_s, 15 * 60)
        with self.assertRaisesMessage(RuleError, "Le temps est écoulé"):
            photos.add_photo(session.photo_upload, jpeg(), now=self.at(15 * 60 + 75))

    def test_submitting_sends_the_photos_to_review(self):
        session = self.session()
        self.photograph(session, 100)
        self.photograph(session, 200)
        submit(session, ai_usage="relecture", now=self.at(300))

        self.assertEqual(session.status, Status.SUBMITTED)
        self.assertIsNone(session.answer_correct)
        solution = session.solution
        self.assertEqual(
            (solution.origin, solution.status, solution.ai_usage, solution.body, solution.photos.count()),
            (Solution.Origin.TRAINING, Solution.Status.UNDER_REVIEW, "relecture", "", 2),
        )
        with self.assertRaises(RuleError):
            save(session, now=self.at(310))

    def test_without_photos_nothing_is_sent_to_review(self):
        session = self.session()
        photo_upload(session, now=self.at(10))
        submit(session, now=self.at(60))
        self.assertIsNone(session.solution)

    def test_abandoning_ends_the_session(self):
        session = self.session()
        abandon(session, now=self.at(30))
        self.assertEqual(session.status, Status.ABANDONED)
        self.assertNotEqual(self.session().pk, session.pk)

    def test_self_rating_refines_the_estimated_difficulty(self):
        for name, rating in [("a", 2), ("b", 4)]:
            session = self.session(user=make_user(name))
            submit(session, now=self.at(60))
            rate(session, rating)
        self.exercise.refresh_from_db()
        self.assertEqual((self.exercise.difficulty_estimated, self.exercise.difficulty_ratings), (3, 2))
        with self.assertRaises(RuleError):
            rate(session, 5)

    def test_median_time_of_other_sessions(self):
        for name, seconds in [("a", 100), ("b", 300), ("c", 200)]:
            session = self.session(user=make_user(name))
            for second in range(10, seconds + 1, 10):
                save(session, now=self.at(second))
            submit(session, now=self.at(seconds))
        self.assertEqual(median_elapsed_s(self.exercise), 200)
        self.assertEqual(median_elapsed_s(self.exercise, exclude=session), 200)


@override_settings(MEDIA_ROOT=MEDIA)
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
        self.assertEqual((session["status"], session["pauses_left"], session["photo_count"]), ("en_cours", 2, 0))
        self.assertLessEqual(session["remaining_s"], 15 * 60)
        url = f"/api/training/sessions/{session['id']}"

        saved = self.post(f"{url}/save", {"focus_losses": 1}).json()
        self.assertEqual(saved["focus_losses"], 1)
        self.assertEqual(self.post(f"{url}/pause").json()["status"], "en_pause")
        self.assertEqual(self.post(f"{url}/resume").json()["status"], "en_cours")

        upload = self.post(f"{url}/photo-upload").json()
        self.assertTrue(upload["timed"] and upload["open"])
        self.assertEqual(self.post(f"{url}/photo-upload").json()["token"], upload["token"])
        sent = self.client.post(
            f"/api/photo-uploads/{upload['token']}/photos",
            {"photo": SimpleUploadedFile("copie.jpg", jpeg(), content_type="image/jpeg")},
        )
        self.assertEqual(sent.status_code, 201)
        self.assertEqual(self.client.get(url).json()["photo_count"], 1)
        # Le temps d'une session ne se prolonge pas, et ses photos ne partent pas ailleurs.
        self.assertEqual(self.post(f"/api/photo-uploads/{upload['token']}/reopen").status_code, 409)
        free = self.post(f"/api/exercises/{self.exercise.pk}/solutions", {"photo_upload": upload["token"]})
        self.assertEqual(free.status_code, 422)

        done = self.post(f"{url}/submit", {"ai_usage": "aucune"}).json()
        self.assertEqual((done["status"], done["solution_status"], done["photo_count"]), ("rendue", "under_review", 1))
        self.assertEqual(self.post(f"{url}/rating", {"rating": 3}).json()["self_rating"], 3)
        late = self.client.post(
            f"/api/photo-uploads/{upload['token']}/photos",
            {"photo": SimpleUploadedFile("copie.jpg", jpeg(), content_type="image/jpeg")},
        )
        self.assertEqual(late.status_code, 410)

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
