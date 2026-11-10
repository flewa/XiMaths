import json

from accounts.services import delete_account
from gamification.services import balance
from notifications.models import Notification

from . import photos
from .models import ModelCopyView, Solution
from .tests import ContentTestCase, make_user

Kind = Notification.Kind


class ModelCopyTests(ContentTestCase):
    """Copie modèle : accord de l'auteur, choix de l'équipe, lecture après sa propre copie."""

    def setUp(self):
        super().setUp()
        # Équipe du site, sans niveau de relecteur : elle n'est pas tirée au sort pour relire.
        self.team = make_user("equipe", is_staff=True)
        self.other = make_user("yanis", level="L1")
        # La copie de Léa, validée, avec son accord.
        self.copy = self.publish()
        self.validate(self.copy)
        self.copy.model_consent = True
        self.copy.save(update_fields=["model_consent"])

    def post(self, user, path, payload=None):
        self.client.force_login(user)
        return self.client.post(f"/api{path}", json.dumps(payload or {}), content_type="application/json")

    def state(self, user=None):
        if user:
            self.client.force_login(user)
        else:
            self.client.logout()
        return self.client.get(f"/api/exercises/{self.exercise.pk}/model-copy").json()

    def choose(self, solution=None, chosen=True):
        return self.post(self.team, f"/solutions/{(solution or self.copy).pk}/model", {"chosen": chosen})

    def test_only_the_team_chooses_among_validated_copies_with_consent(self):
        self.assertEqual(self.post(self.other, f"/solutions/{self.copy.pk}/model", {"chosen": True}).status_code, 403)
        self.assertEqual(self.client.get(f"/api/exercises/{self.exercise.pk}/model-candidates").status_code, 403)

        # Sans accord, ou pas encore validée : la copie n'est pas proposée à l'équipe.
        without_consent = self.publish(author=self.other)
        self.validate(without_consent)
        self.assertEqual(self.choose(without_consent).status_code, 409)

        [candidate] = self.choose().json()
        self.assertEqual((candidate["id"], candidate["is_model"]), (self.copy.pk, True))
        chosen = Notification.objects.get(user=self.student, kind=Kind.SOLUTION_RECOMMENDED)
        self.assertIn("copie modèle", chosen.title)

    def test_the_model_copy_unlocks_once_a_copy_is_sent(self):
        self.choose()
        self.assertEqual(self.state(), {"exists": True, "can_open": False, "opened": False, "costs_points": False, "photos": []})
        self.assertFalse(self.state(self.other)["can_open"])
        self.assertEqual(self.post(self.other, f"/exercises/{self.exercise.pk}/model-copy/open").status_code, 403)
        self.assertFalse(photos.can_view(self.other, self.copy))

        self.publish(author=self.other)
        state = self.state(self.other)
        # Sa copie n'est pas encore validée : ouvrir le modèle privera de points la suivante.
        self.assertEqual((state["can_open"], state["opened"], state["costs_points"]), (True, False, True))
        opened = self.post(self.other, f"/exercises/{self.exercise.pk}/model-copy/open").json()
        self.assertTrue(opened["opened"])
        self.copy.refresh_from_db()
        self.assertTrue(photos.can_view(self.other, self.copy))

    def test_a_copy_sent_after_opening_the_model_earns_no_points(self):
        self.choose()
        first = self.publish(author=self.other)
        self.post(self.other, f"/exercises/{self.exercise.pk}/model-copy/open")
        # La copie envoyée avant d'ouvrir le modèle garde ses points.
        self.validate(first)
        earned = balance(self.other)
        self.assertGreater(earned, 0)

        second = self.publish(author=self.other)
        self.assertTrue(second.after_model)
        self.assertEqual(self.validate(second), Solution.Status.VALIDATED)
        self.assertEqual(balance(self.other), earned)

    def test_withdrawing_consent_removes_the_model_at_once(self):
        self.choose()
        self.publish(author=self.other)
        self.post(self.other, f"/exercises/{self.exercise.pk}/model-copy/open")

        response = self.post(self.student, f"/solutions/{self.copy.pk}/model-consent", {"consent": False})
        self.assertEqual((response.json()["model_consent"], response.json()["is_model"]), (False, False))
        self.assertFalse(self.state(self.other)["exists"])
        self.copy.refresh_from_db()
        self.assertFalse(photos.can_view(self.other, self.copy))
        # Seul l'auteur décide de son accord.
        self.assertEqual(self.post(self.other, f"/solutions/{self.copy.pk}/model-consent", {"consent": True}).status_code, 404)

    def test_one_model_per_exercise_and_the_team_can_take_it_back(self):
        second = self.publish(author=self.other)
        self.validate(second)
        second.model_consent = True
        second.save(update_fields=["model_consent"])
        self.choose()
        self.choose(second)
        self.assertEqual(list(Solution.objects.filter(model_at__isnull=False)), [second])
        self.choose(second, chosen=False)
        self.assertFalse(self.state(self.team)["exists"])

    def test_deleting_the_account_ends_the_consent(self):
        self.choose()
        delete_account(self.student)
        self.copy.refresh_from_db()
        self.assertEqual((self.copy.model_consent, self.copy.model_at), (False, None))
        self.assertFalse(ModelCopyView.objects.filter(user=self.student).exists())
