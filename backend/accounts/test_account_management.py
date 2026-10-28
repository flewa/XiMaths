import re
from unittest import mock
from urllib.parse import parse_qs, urlparse

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from catalog.models import Level
from content.models import Exercise

from .models import User

PASSWORD = "une-phrase-solide"
NEW_PASSWORD = "une-autre-phrase-solide"


class AccountTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "lea", "lea@example.com", PASSWORD, email_verified_at=timezone.now()
        )

    def post(self, url, data=None):
        return self.client.post(url, data or {}, content_type="application/json")


class PasswordTests(AccountTestCase):
    def test_reset_by_email_then_the_link_works_once(self):
        self.assertEqual(self.post("/api/auth/password-reset", {"email": "LEA@example.com"}).status_code, 204)
        [message] = mail.outbox
        link = re.search(r"https?://\S+", message.body)[0]
        query = parse_qs(urlparse(link).query)
        payload = {"uid": query["uid"][0], "token": query["token"][0], "password": NEW_PASSWORD}

        self.assertEqual(self.post("/api/auth/password-reset/confirm", payload).status_code, 204)
        self.assertEqual(self.post("/api/auth/password-reset/confirm", payload).status_code, 400)
        self.assertEqual(self.post("/api/auth/login", {"login": "lea", "password": NEW_PASSWORD}).status_code, 200)

    def test_an_unknown_address_gets_the_same_answer_and_no_email(self):
        self.assertEqual(self.post("/api/auth/password-reset", {"email": "personne@example.com"}).status_code, 204)
        self.assertEqual(mail.outbox, [])

    def test_changing_the_password_keeps_the_session(self):
        self.client.force_login(self.user)
        wrong = self.post("/api/auth/password", {"current_password": "faux", "new_password": NEW_PASSWORD})
        self.assertEqual(wrong.status_code, 403)

        ok = self.post("/api/auth/password", {"current_password": PASSWORD, "new_password": NEW_PASSWORD})

        self.assertEqual(ok.status_code, 204)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 200)


class SettingsTests(AccountTestCase):
    def test_preferences_change_only_what_is_sent(self):
        self.client.force_login(self.user)
        me = self.post("/api/auth/preferences", {"declared_level": "MPSI", "weekly_digest": True}).json()
        self.assertEqual((me["declared_level"], me["weekly_digest"], me["email_notifications"]), ("MPSI", True, True))

        me = self.post("/api/auth/preferences", {"declared_level": ""}).json()
        self.assertIsNone(me["declared_level"])
        self.assertEqual(self.post("/api/auth/preferences", {"declared_level": "XX"}).status_code, 422)

    def test_export_contains_my_contributions(self):
        Exercise.objects.create(
            author=self.user,
            title="Mon exercice",
            statement="Énoncé.",
            difficulty_declared=1,
            primary_level=Level.objects.get(code="L1"),
        )
        self.client.force_login(self.user)

        response = self.client.get("/api/auth/export")

        self.assertIn("attachment", response["Content-Disposition"])
        data = response.json()
        self.assertEqual(data["compte"]["pseudo"], "lea")
        self.assertEqual([e["titre"] for e in data["exercices"]], ["Mon exercice"])

    def test_deleting_the_account_keeps_contributions_anonymously(self):
        exercise = Exercise.objects.create(
            author=self.user,
            title="Mon exercice",
            statement="Énoncé.",
            difficulty_declared=1,
            primary_level=Level.objects.get(code="L1"),
        )
        self.client.force_login(self.user)
        self.assertEqual(self.post("/api/auth/delete", {"confirmation": "oui", "password": PASSWORD}).status_code, 422)
        self.assertEqual(
            self.post("/api/auth/delete", {"confirmation": "SUPPRIMER", "password": "faux"}).status_code, 403
        )

        response = self.post("/api/auth/delete", {"confirmation": "SUPPRIMER", "password": PASSWORD})

        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        exercise.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertNotIn("lea", self.user.email)
        self.assertIsNone(exercise.author)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)


@override_settings(GOOGLE_CLIENT_ID="client-test", GOOGLE_CLIENT_SECRET="secret-test")
class GoogleTests(AccountTestCase):
    def start(self):
        response = self.client.get("/api/auth/google/start", {"next": "/classements"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("https://accounts.google.com/"))
        return parse_qs(urlparse(response["Location"]).query)["state"][0]

    def callback(self, claims, state):
        with mock.patch("accounts.google.exchange_code", return_value=claims):
            return self.client.get("/api/auth/google/callback", {"code": "code", "state": state})

    def test_a_new_google_account_is_created_already_verified(self):
        response = self.callback({"sub": "g-1", "email": "Marie.Curie@gmail.com", "email_verified": True}, self.start())

        self.assertEqual(response["Location"], "http://localhost:3000/classements")
        me = self.client.get("/api/auth/me").json()
        self.assertEqual((me["username"], me["email_verified"], me["has_password"]), ("marie.curie", True, False))

    def test_an_existing_address_is_linked(self):
        self.callback({"sub": "g-2", "email": "lea@example.com", "email_verified": True}, self.start())
        self.user.refresh_from_db()
        self.assertEqual(self.user.google_sub, "g-2")
        self.assertEqual(self.client.get("/api/auth/me").json()["username"], "lea")

    def test_a_forged_state_is_refused(self):
        self.start()
        response = self.callback({"sub": "g-3", "email": "x@gmail.com", "email_verified": True}, "faux")
        self.assertEqual(response["Location"], "http://localhost:3000/connexion?erreur=google")
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)

    def test_providers_follow_the_configuration(self):
        self.assertEqual(self.client.get("/api/auth/providers").json(), {"google": True})
        with override_settings(GOOGLE_CLIENT_ID=""):
            self.assertEqual(self.client.get("/api/auth/providers").json(), {"google": False})
