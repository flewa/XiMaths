import json

from django.core.cache import cache

from gamification.services import balance
from moderation.models import ModerationLog, Report
from notifications.models import Notification

from .models import Exercise, Solution
from .tests import ContentTestCase, Verdict, make_user

Action = ModerationLog.Action


class PanelActionTests(ContentTestCase):
    """Le panneau agit : chaque action est motivée, notifiée et inscrite au journal."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.admin = make_user("admin", is_staff=True, level=None)

    def post(self, path, payload=None, user=None):
        self.client.force_login(user or self.admin)
        return self.client.post(f"/api/panel/{path}", json.dumps(payload or {}), content_type="application/json")

    def logged(self, action):
        return ModerationLog.objects.filter(action=action, actor=self.admin).exists()

    def test_validating_a_copy_pays_its_author_and_is_logged(self):
        solution = self.publish()
        response = self.post(f"solutions/{solution.pk}/decide", {"decision": "validate", "reason": "Copie juste."})
        self.assertEqual(response.status_code, 204)
        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.VALIDATED)
        self.assertGreater(balance(self.student), 0)
        self.assertTrue(self.logged(Action.SOLUTION_DECIDED))

    def test_sending_back_a_validated_copy_takes_its_points_back(self):
        solution = self.publish()
        self.validate(solution)
        self.assertGreater(balance(self.student), 0)
        self.post(f"solutions/{solution.pk}/decide", {"decision": "needs_work", "reason": "Une étape fausse."})
        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.NEEDS_WORK)
        self.assertEqual(balance(self.student), 0)
        self.assertTrue(Notification.objects.filter(user=self.student, body__contains="Une étape fausse.").exists())

        # Puis la remettre en relecture : un nouveau tour, de nouveaux relecteurs.
        self.post(f"solutions/{solution.pk}/decide", {"decision": "review_again", "reason": "Deuxième avis."})
        solution.refresh_from_db()
        self.assertEqual((solution.status, solution.review_round), (Solution.Status.UNDER_REVIEW, 2))

    def test_removing_a_copy_is_an_appealable_decision_without_reward(self):
        solution = self.publish()
        self.post(f"solutions/{solution.pk}/decide", {"decision": "remove_plagiarism", "reason": "Recopiée d'un livre."})
        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.HIDDEN)
        # Le signalement de l'administrateur ne lui rapporte rien, et il n'en est pas prévenu.
        self.assertEqual(balance(self.admin), 0)
        self.assertFalse(Notification.objects.filter(user=self.admin).exists())
        self.client.force_login(self.student)
        [decision] = self.client.get("/api/decisions/mine").json()
        self.assertEqual((decision["type"], decision["can_appeal"]), ("report", True))

    def test_guard_rails(self):
        solution = self.publish()
        self.assertEqual(self.post(f"solutions/{solution.pk}/decide", {"decision": "validate", "reason": "x"}, self.student).status_code, 403)
        self.assertEqual(self.post(f"solutions/{solution.pk}/decide", {"decision": "validate", "reason": " "}).status_code, 422)
        self.assertEqual(self.post(f"solutions/{solution.pk}/decide", {"decision": "review_again", "reason": "x"}).status_code, 409)
        own = Solution.objects.create(exercise=self.exercise, author=self.admin, status=Solution.Status.UNDER_REVIEW)
        self.assertEqual(self.post(f"solutions/{own.pk}/decide", {"decision": "validate", "reason": "x"}).status_code, 403)

    def test_editing_an_exercise_and_removing_then_restoring_it(self):
        self.client.force_login(self.admin)
        detail = self.client.get(f"/api/panel/exercises/{self.exercise.pk}").json()
        detail.update(title="Série de Riemann (énoncé corrigé)", statement="Montrer que la série des 1/n^2 converge, puis majorer sa somme.", reason="Coquille dans l'énoncé.")
        response = self.client.put(f"/api/panel/exercises/{self.exercise.pk}", json.dumps(detail), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.exercise.refresh_from_db()
        self.assertEqual(self.exercise.title, "Série de Riemann (énoncé corrigé)")
        self.assertIsNotNone(self.exercise.edited_by_team_at)
        self.assertTrue(self.logged(Action.EXERCISE_EDITED))

        points = balance(self.author)
        self.post(f"exercises/{self.exercise.pk}/status", {"action": "remove_inappropriate", "reason": "Hors sujet."})
        self.exercise.refresh_from_db()
        self.assertEqual(self.exercise.status, Exercise.Status.REMOVED)
        self.assertLess(balance(self.author), points)
        self.assertTrue(Report.objects.filter(reporter=self.admin, status=Report.Status.CONFIRMED).exists())

        self.post(f"exercises/{self.exercise.pk}/status", {"action": "restore", "reason": "Erreur de ma part."})
        self.exercise.refresh_from_db()
        self.assertEqual(self.exercise.status, Exercise.Status.PUBLISHED)
        self.assertEqual(balance(self.author), points)

    def test_account_actions(self):
        lea = self.student.username
        self.assertEqual(self.post(f"members/{lea}/points", {"amount": 25, "reason": "Aide sur le Discord."}).status_code, 200)
        self.assertEqual(balance(self.student), 25)
        self.post(f"members/{lea}/points", {"amount": -5, "reason": "Correction."})
        self.assertEqual(balance(self.student), 20)

        self.post(f"members/{lea}/trust", {"level": 2, "reason": "Relectures sérieuses."})
        self.assertEqual(self.post(f"members/{lea}/trust", {"level": 2, "reason": "x"}).status_code, 409)
        self.student.refresh_from_db()
        self.assertEqual(self.student.trust_level, 2)

        self.student.email_verified_at = None
        self.student.save(update_fields=["email_verified_at"])
        self.post(f"members/{lea}/verify-email")
        self.student.refresh_from_db()
        self.assertIsNotNone(self.student.email_verified_at)

        self.assertEqual(self.post(f"members/{lea}/rename", {"username": "relecteur0", "reason": "x"}).status_code, 409)
        self.post(f"members/{lea}/rename", {"username": "lea-xi", "reason": "Pseudo trompeur."})
        self.student.refresh_from_db()
        self.assertEqual(self.student.username, "lea-xi")

        self.assertEqual(self.post("members/lea-xi/delete", {"confirm": "lea", "reason": "Doublon."}).status_code, 422)
        self.assertEqual(self.post("members/lea-xi/delete", {"confirm": "lea-xi", "reason": "Compte en double."}).status_code, 200)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)
        for action in [Action.POINTS_ADJUSTED, Action.TRUST_CHANGED, Action.EMAIL_VERIFIED, Action.ACCOUNT_RENAMED, Action.ACCOUNT_DELETED]:
            self.assertTrue(self.logged(action), action)

    def test_only_the_owner_names_administrators_and_no_one_acts_on_themselves(self):
        other = make_user("admin2", is_staff=True, level=None)
        self.assertEqual(self.post(f"members/{self.student.username}/admin", {"admin": True}).status_code, 403)
        self.assertEqual(self.post(f"members/{other.username}/points", {"amount": 5, "reason": "x"}).status_code, 403)
        self.assertEqual(self.post(f"members/{self.admin.username}/points", {"amount": 5, "reason": "x"}).status_code, 403)

        owner = make_user("proprietaire", is_staff=True, is_superuser=True, level=None)
        self.assertEqual(self.post(f"members/{self.student.username}/admin", {"admin": True}, owner).status_code, 200)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_staff)
        self.client.force_login(owner)
        file = self.client.get(f"/api/moderation/members/{self.student.username}").json()
        self.assertTrue(file["can_administer"] and file["can_make_admin"])
