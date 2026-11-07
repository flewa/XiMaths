import random
import shutil
import tempfile
from datetime import timedelta

from django.test import override_settings
from django.utils import timezone

from config.errors import RuleError
from content import photos
from content.models import Exercise, Review, Solution
from content.services import submit_review
from content.test_photos import jpeg
from content.tests import ContentTestCase, make_user
from gamification.models import PointTransaction, UserBadge
from notifications.models import Notification

from . import challenges, services
from .models import Challenge, ChallengeTemplate, TimedSession

Reason = PointTransaction.Reason
MEDIA = tempfile.mkdtemp(prefix="ximaths-defi-")


class ChallengeTestCase(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.exercise.difficulty_declared = 2  # m(d) = 1,25 : 25 points au barème du défi
        self.exercise.hints = ["Pense à la règle de d'Alembert.", "Le rapport tend vers |x|/b."]
        self.exercise.save()
        self.template = ChallengeTemplate.objects.create(
            exercise=self.exercise,
            statement="Rayon de convergence de $\\sum n^{{a}} x^n / {{b}}^n$ ?",
            parameters={"a": [2, 3], "b": [3, 5, 7]},
            answer="b",
        )
        self.now = timezone.now()
        self.challenge = challenges.open_challenges(now=self.now, rng=random.Random(0))[0]

    def start(self, user=None, **kwargs):
        return challenges.start(user or self.student, self.challenge, rng=random.Random(1), now=self.now, **kwargs)


class OpeningTests(ChallengeTestCase):
    def test_one_challenge_per_level_and_day_with_opt_in_notifications(self):
        self.assertEqual(self.challenge.level, self.exercise.primary_level)
        self.assertEqual(self.challenge.closes_at - self.challenge.opens_at, timedelta(days=1))
        self.assertEqual(challenges.open_challenges(now=self.now), [])

        fan = make_user("fan", level="L1", daily_challenge_notifications=True)
        tomorrow = self.now + timedelta(days=1)
        challenges.open_challenges(now=tomorrow)
        self.assertTrue(Notification.objects.filter(user=fan, kind=Notification.Kind.CHALLENGE).exists())
        self.assertFalse(Notification.objects.filter(user=self.student, kind=Notification.Kind.CHALLENGE).exists())

    def test_a_template_is_checked_before_use(self):
        broken = ChallengeTemplate(statement="Calculer {{c}}.", parameters={"e": [1], "a": "2"}, answer="a+")
        errors = challenges.check_template(broken)
        self.assertEqual(len(errors), 3)
        self.assertEqual(challenges.check_template(self.template), [])


class SessionTests(ChallengeTestCase):
    def test_each_member_gets_their_own_parameters(self):
        session = self.start()
        b = session.parameters["b"]
        self.assertIn(f"/ {b}^n", challenges.statement(session))
        self.assertNotIn("{{", challenges.statement(session))
        self.assertEqual(challenges.expected(session), f"({b})")

    def test_one_attempt_even_after_abandoning(self):
        session = self.start()
        services.abandon(session, now=self.now)
        self.assertEqual(self.start().pk, session.pk)
        self.assertEqual(TimedSession.objects.filter(challenge=self.challenge).count(), 1)

    def test_the_clock_never_stops_and_there_is_no_pause(self):
        session = self.start()
        later = self.now + timedelta(minutes=10)
        # Aucun signe de vie pendant 10 minutes : le temps compte quand même.
        self.assertAlmostEqual(services.remaining_s(session, later), 20 * 60)
        with self.assertRaises(RuleError):
            services.pause(session, now=later)

    def test_a_closed_challenge_cannot_start(self):
        with self.assertRaises(RuleError):
            challenges.start(self.student, self.challenge, now=self.challenge.closes_at)

    def test_hints_are_sent_once_opened(self):
        session = self.start()
        self.assertEqual(session.hints_opened, 0)
        challenges.open_hint(session)
        challenges.open_hint(session)
        challenges.open_hint(session)
        self.assertEqual(session.hints_opened, 2)


@override_settings(MEDIA_ROOT=MEDIA)
class ScoringTests(ChallengeTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def photograph(self, session, *, minutes):
        upload = services.photo_upload(session, now=self.now + timedelta(minutes=minutes))
        return photos.add_photo(upload, jpeg(), now=self.now + timedelta(minutes=minutes))

    def submit(self, session, *, minutes=15):
        self.photograph(session, minutes=minutes - 1)
        return services.submit(session, now=self.now + timedelta(minutes=minutes))

    def test_all_the_points_wait_for_the_copy_to_be_validated(self):
        session = self.submit(self.start())

        # Mi-temps : bonus ×1,125. 25 × 1,125 = 28,125 → 28 ; rien n'est versé au rendu.
        self.assertAlmostEqual(session.bonus, 1.125)
        self.assertEqual((session.answer_points, session.justification_points), (0, 28))
        self.assertFalse(PointTransaction.objects.filter(user=self.student, reason=Reason.CHALLENGE_ANSWER).exists())

        for review in session.solution.reviews.all():
            submit_review(review, Review.Verdict.CORRECT)

        session.solution.refresh_from_db()
        self.assertEqual(session.solution.status, Solution.Status.VALIDATED)
        txn = PointTransaction.objects.get(user=self.student, reason=Reason.CHALLENGE_JUSTIFIED)
        self.assertEqual(txn.amount, 28)
        self.assertFalse(PointTransaction.objects.filter(user=self.student, reason=Reason.SOLUTION_VALIDATED).exists())

    def test_each_hint_cuts_the_bonus_by_ten_percent(self):
        session = self.start()
        challenges.open_hint(session)
        session = self.submit(session)
        self.assertAlmostEqual(session.bonus, 1 + 0.25 * 0.5 * 0.9)

    def test_the_copy_goes_to_review_with_the_drawn_statement(self):
        session = self.submit(self.start())
        solution = session.solution
        self.assertEqual(solution.origin, Solution.Origin.DAILY)
        self.assertEqual(solution.ai_usage, Solution.AiUsage.NONE)
        self.assertEqual(solution.photos.count(), 1)
        self.assertIn(f"{session.parameters['b']}^n", solution.variant_statement)

    def test_photos_must_arrive_within_the_thirty_minutes_and_the_grace(self):
        session = self.start()
        self.photograph(session, minutes=30.5)
        with self.assertRaisesMessage(RuleError, "Le temps est écoulé"):
            self.photograph(session, minutes=31.1)

    def test_without_photos_nothing_is_sent_and_nothing_is_earned(self):
        session = services.submit(self.start(), now=self.now + timedelta(minutes=10))
        self.assertIsNone(session.solution)
        self.assertFalse(PointTransaction.objects.filter(user=self.student, reason__startswith="challenge").exists())

    def test_an_abandoned_tab_is_submitted_after_the_deadline_with_its_photos(self):
        session = self.start()
        self.photograph(session, minutes=5)
        services.save(session, now=self.now + timedelta(minutes=5))

        self.assertEqual(services.close_expired(now=self.now + timedelta(minutes=20)), 0)
        self.assertEqual(services.close_expired(now=self.now + timedelta(minutes=32)), 1)
        session.refresh_from_db()
        self.assertEqual(session.status, TimedSession.Status.SUBMITTED)
        self.assertEqual(session.solution.photos.count(), 1)

    def test_five_validated_challenges_earn_under_pressure(self):
        for day in range(5):
            challenge = Challenge.objects.create(
                level=self.challenge.level,
                date=self.challenge.date - timedelta(days=day + 1),
                template=self.template,
                opens_at=self.now - timedelta(hours=1),
                closes_at=self.now + timedelta(hours=1),
            )
            session = challenges.start(self.student, challenge, now=self.now)
            session = self.submit(session)
            Solution.objects.filter(pk=session.solution_id).update(status=Solution.Status.VALIDATED)
        from gamification.badges import check_badges

        check_badges(self.student)
        self.assertTrue(UserBadge.objects.filter(user=self.student, badge="sous-pression").exists())


@override_settings(MEDIA_ROOT=MEDIA)
class ChallengeApiTests(ChallengeTestCase):
    def setUp(self):
        super().setUp()
        self.student.email_verified_at = timezone.now()
        self.student.save()
        self.client.force_login(self.student)

    def test_today_lists_the_challenge_without_its_statement(self):
        [item] = self.client.get("/api/challenges/today").json()
        self.assertEqual(item["level"], self.challenge.level.code)
        self.assertEqual(item["points_max"], 31)  # 25 × 1,25, bonus de rapidité compris
        self.assertIsNone(item["attempt"])
        self.assertNotIn("statement", item)

    def test_starting_sends_the_drawn_statement_and_no_hint(self):
        response = self.client.post(f"/api/challenges/{self.challenge.pk}/start")
        self.assertEqual(response.status_code, 201)
        session = response.json()
        self.assertEqual(session["kind"], "defi")
        self.assertEqual(session["hints"], [])
        self.assertEqual(session["hint_count"], 2)
        self.assertEqual(session["pauses_left"], 0)

        opened = self.client.post(f"/api/training/sessions/{session['id']}/hint").json()
        self.assertEqual(len(opened["hints"]), 1)
        self.assertEqual(self.client.get("/api/challenges/today").json()[0]["attempt"]["session_id"], session["id"])

    def submitted(self):
        session = self.start()
        photos.add_photo(services.photo_upload(session, now=self.now), jpeg(), now=self.now)
        return services.submit(session, now=self.now)

    def test_reviewers_see_the_answer_expected_for_the_drawn_parameters(self):
        session = self.submitted()
        reviewer = session.solution.reviews.first().reviewer
        self.client.force_login(reviewer)

        [task] = self.client.get("/api/reviews").json()

        self.assertEqual(task["expected_answer"], f"({session.parameters['b']})")
        self.assertEqual(len(task["solution_photos"]), 1)

    def test_challenge_solutions_stay_hidden_until_the_window_closes(self):
        session = self.submitted()
        Solution.objects.filter(pk=session.solution_id).update(status=Solution.Status.VALIDATED, validated_at=self.now)

        detail = self.client.get(f"/api/exercises/{self.exercise.pk}").json()
        self.assertEqual(detail["solutions"], [])
        Challenge.objects.filter(pk=self.challenge.pk).update(closes_at=self.now - timedelta(seconds=1))
        detail = self.client.get(f"/api/exercises/{self.exercise.pk}").json()
        self.assertEqual(len(detail["solutions"]), 1)
        self.assertIn("^n", detail["solutions"][0]["variant_statement"])


class TemplateAdminFormTests(ChallengeTestCase):
    def test_the_admin_form_reports_template_errors(self):
        from .admin import ChallengeTemplateForm

        other = Exercise.objects.create(
            author=self.author, title="Autre", statement="Énoncé.", difficulty_declared=1,
            primary_level=self.exercise.primary_level, status=Exercise.Status.PUBLISHED,
        )
        form = ChallengeTemplateForm(
            data={"exercise": other.pk, "statement": "{{z}}", "parameters": '{"a": [1]}', "answer": "a", "active": True}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.non_field_errors()), 1)
