from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from config.errors import RuleError
from content.models import Exercise, Solution
from content.tests import TL, ContentTestCase, make_user
from gamification.models import PointTransaction
from gamification.rankings import absence_reason, standings
from gamification.services import award, balance
from gamification.trust import promote
from notifications.models import Notification

from .models import Appeal, Report, Sanction
from .services import create_appeal, decide_appeal, lift_expired, resolve_report, sanction


def give_points(user, amount):
    PointTransaction.objects.create(
        user=user, amount=amount, reason=PointTransaction.Reason.SOLUTION_VALIDATED, source_type="test", source_id=user.pk
    )


class SanctionTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.moderator = make_user("modo", is_staff=True)
        self.other_moderator = make_user("modo2", is_staff=True)

    def test_a_suspension_lasts_seven_days_and_is_notified(self):
        now = timezone.now()
        decision = sanction(
            self.student, Sanction.Kind.SUSPENSION, reason="Plagiat répété.", moderator=self.moderator, now=now
        )

        self.student.refresh_from_db()
        self.assertEqual(self.student.status, "suspended")
        self.assertEqual(decision.ends_at, now + timedelta(days=7))
        self.assertTrue(Notification.objects.filter(user=self.student, kind=Notification.Kind.SANCTION).exists())

        self.assertEqual(lift_expired(now=now + timedelta(days=8)), 1)
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, "active")

    def test_only_moderators_sanction_and_always_with_a_reason(self):
        with self.assertRaises(PermissionDenied):
            sanction(self.student, Sanction.Kind.WARNING, reason="Motif.", moderator=self.author)
        with self.assertRaises(RuleError):
            sanction(self.student, Sanction.Kind.WARNING, reason="  ", moderator=self.moderator)

    def test_a_leaderboard_ban_hides_the_member_from_the_rankings(self):
        give_points(self.student, 40)
        self.assertIn(self.student.pk, [entry.user_id for entry in standings()])

        sanction(self.student, Sanction.Kind.LEADERBOARD_BAN, reason="Points gonflés.", moderator=self.moderator)

        self.assertNotIn(self.student.pk, [entry.user_id for entry in standings()])
        self.assertIn("sanction", absence_reason(self.student))


class TrustTests(ContentTestCase):
    def validated_solutions(self, user, count):
        for index in range(count):
            exercise = Exercise.objects.create(
                author=self.author,
                title=f"Exercice {index}",
                statement="Énoncé.",
                difficulty_declared=2,
                primary_level=self.exercise.primary_level,
                status=Exercise.Status.PUBLISHED,
            )
            Solution.objects.create(exercise=exercise, author=user, body="Preuve.", status=Solution.Status.VALIDATED)

    def test_a_member_becomes_reviewer_with_points_and_validated_solutions(self):
        give_points(self.student, 300)
        self.validated_solutions(self.student, 4)
        self.assertIsNone(promote(self.student))

        self.validated_solutions(self.student, 1)

        self.assertEqual(promote(self.student), TL.REVIEWER)
        self.student.refresh_from_db()
        self.assertEqual(self.student.trust_level, TL.REVIEWER)
        self.assertTrue(Notification.objects.filter(user=self.student, kind=Notification.Kind.PROMOTION).exists())

    def test_a_recent_sanction_delays_the_promotion(self):
        give_points(self.student, 300)
        self.validated_solutions(self.student, 5)
        sanction(self.student, Sanction.Kind.WARNING, reason="Ton agressif.", moderator=make_user("m", is_staff=True))

        self.assertIsNone(promote(self.student))
        self.assertEqual(promote(self.student, now=timezone.now() + timedelta(days=91)), TL.REVIEWER)

    def test_moderators_are_never_promoted_or_demoted(self):
        moderator = make_user("modo", trust=TL.MODERATOR)
        give_points(moderator, 5000)
        self.assertIsNone(promote(moderator))


class AppealTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.moderator = make_user("modo", is_staff=True)
        self.other_moderator = make_user("modo2", is_staff=True)

    def remove_solution(self):
        solution = self.publish()
        award(self.student, PointTransaction.Reason.SOLUTION_VALIDATED, solution, amount=15)
        self.earned = balance(self.student)
        report = Report.objects.create(reporter=self.author, solution=solution, reason=Report.Reason.INAPPROPRIATE)
        resolve_report(report, confirmed=True, moderator=self.moderator, note="Propos insultants.")
        report.refresh_from_db()
        return solution, report

    def test_an_overturned_sanction_is_lifted(self):
        decision = sanction(self.student, Sanction.Kind.SUSPENSION, reason="Erreur.", moderator=self.moderator)
        appeal = create_appeal(self.student, decision, "Ce n'était pas moi, mon compte était partagé.")

        with self.assertRaises(PermissionDenied):
            decide_appeal(appeal, overturn=True, moderator=self.moderator, note="Je me suis trompé.")
        decide_appeal(appeal, overturn=True, moderator=self.other_moderator, note="Preuves insuffisantes.")

        decision.refresh_from_db()
        self.student.refresh_from_db()
        self.assertIsNotNone(decision.lifted_at)
        self.assertEqual(self.student.status, "active")
        self.assertTrue(Notification.objects.filter(user=self.student, kind=Notification.Kind.APPEAL_DECIDED).exists())

    def test_an_overturned_removal_restores_the_content_and_its_points(self):
        solution, report = self.remove_solution()
        self.assertLess(balance(self.student), self.earned)

        appeal = create_appeal(self.student, report, "Le ton était vif mais pas insultant.")
        decide_appeal(appeal, overturn=True, moderator=self.other_moderator, note="Ton vif, pas insultant.")

        solution.refresh_from_db()
        self.assertNotEqual(solution.status, Solution.Status.HIDDEN)
        self.assertEqual(balance(self.student), self.earned)

    def test_an_upheld_decision_stays(self):
        _, report = self.remove_solution()
        appeal = create_appeal(self.student, report, "Je conteste cette décision.")
        decide_appeal(appeal, overturn=False, moderator=self.other_moderator, note="Les propos sont insultants.")
        report.solution.refresh_from_db()
        self.assertEqual(report.solution.status, Solution.Status.HIDDEN)
        self.assertEqual(Appeal.objects.get().status, Appeal.Status.UPHELD)

    def test_appeals_are_limited_to_the_owner_once_within_fourteen_days(self):
        decision = sanction(self.student, Sanction.Kind.WARNING, reason="Spam.", moderator=self.moderator)
        with self.assertRaises(PermissionDenied):
            create_appeal(self.author, decision, "Ce n'est pas ma sanction.")
        with self.assertRaises(RuleError):
            create_appeal(self.student, decision, "Trop tard.", now=timezone.now() + timedelta(days=15))
        create_appeal(self.student, decision, "Je conteste l'avertissement.")
        with self.assertRaises(RuleError):
            create_appeal(self.student, decision, "Une seconde fois.")


class DecisionsApiTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.moderator = make_user("modo", is_staff=True)
        self.client.force_login(self.student)

    def test_my_decisions_list_sanctions_and_removals_with_the_appeal_state(self):
        sanction(self.student, Sanction.Kind.WARNING, reason="Spam répété.", moderator=self.moderator)
        solution = self.publish()
        report = Report.objects.create(reporter=self.author, solution=solution, reason=Report.Reason.INAPPROPRIATE)
        resolve_report(report, confirmed=True, moderator=self.moderator, note="Propos insultants.")

        decisions = self.client.get("/api/decisions/mine").json()

        self.assertEqual({item["type"] for item in decisions}, {"sanction", "report"})
        self.assertTrue(all(item["can_appeal"] for item in decisions))
        removal = next(item for item in decisions if item["type"] == "report")
        self.assertEqual(removal["reason"], "Propos insultants.")

    def test_appealing_through_the_api(self):
        decision = sanction(self.student, Sanction.Kind.WARNING, reason="Spam.", moderator=self.moderator)
        payload = {"type": "sanction", "id": decision.pk, "statement": "Je n'ai rien publié de tel."}

        self.assertEqual(self.client.post("/api/appeals", payload, content_type="application/json").status_code, 201)
        self.assertEqual(self.client.post("/api/appeals", payload, content_type="application/json").status_code, 409)

        item = self.client.get("/api/decisions/mine").json()[0]
        self.assertFalse(item["can_appeal"])
        self.assertEqual(item["appeal_status"], Appeal.Status.PENDING)
