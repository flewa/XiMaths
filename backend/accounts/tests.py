import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase

User = get_user_model()
PASSWORD = "une-phrase-solide"


def post(client, url, data=None, **extra):
    return client.post(url, data or {}, content_type="application/json", **extra)


class AuthApiTests(TestCase):
    def setUp(self):
        cache.clear()  # remet à zéro la limitation de débit

    def signup(self, **fields):
        data = {
            "username": "lea",
            "email": "Lea@Example.com",
            "password": PASSWORD,
            "declared_level": "L1",
            **fields,
        }
        return post(self.client, "/api/auth/signup", data)

    def token_from_email(self):
        return re.search(r"token=(\S+)", mail.outbox[-1].body).group(1)

    def test_signup_logs_in_and_sends_a_verification_link(self):
        self.assertEqual(self.signup().status_code, 201)

        me = self.client.get("/api/auth/me").json()

        self.assertEqual(me["username"], "lea")
        self.assertEqual(me["email"], "lea@example.com")
        self.assertEqual(me["declared_level"], "L1")
        self.assertFalse(me["email_verified"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/verifier-email?token=", mail.outbox[0].body)

    def test_the_verification_link_verifies_the_email(self):
        self.signup()
        response = post(self.client, "/api/auth/verify-email", {"token": self.token_from_email()})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["email_verified"])

    def test_a_tampered_token_is_refused(self):
        self.signup()
        response = post(self.client, "/api/auth/verify-email", {"token": "abc:def"})
        self.assertEqual(response.status_code, 400)

    def test_the_link_breaks_if_the_email_changes(self):
        self.signup()
        token = self.token_from_email()
        User.objects.filter(username="lea").update(email="autre@example.com")
        response = post(self.client, "/api/auth/verify-email", {"token": token})
        self.assertEqual(response.status_code, 400)

    def test_a_taken_pseudo_or_email_is_refused(self):
        self.signup()
        self.assertEqual(self.signup(email="autre@example.com").status_code, 409)
        self.assertEqual(self.signup(username="lea2", email="LEA@example.com").status_code, 409)

    def test_a_weak_password_is_refused(self):
        response = self.signup(password="12345678")
        self.assertEqual(response.status_code, 422)
        self.assertTrue(response.json()["detail"])

    def test_login_accepts_the_pseudo_or_the_email(self):
        User.objects.create_user("yanis", "yanis@example.com", PASSWORD)
        for login in ("yanis", "YANIS@example.com"):
            with self.subTest(login=login):
                response = post(Client(), "/api/auth/login", {"login": login, "password": PASSWORD})
                self.assertEqual(response.status_code, 200)

    def test_a_wrong_password_is_refused(self):
        User.objects.create_user("yanis", "yanis@example.com", PASSWORD)
        response = post(self.client, "/api/auth/login", {"login": "yanis", "password": "faux"})
        self.assertEqual(response.status_code, 401)

    def test_a_suspended_account_cannot_log_in(self):
        User.objects.create_user("yanis", "yanis@example.com", PASSWORD, status="suspended")
        response = post(self.client, "/api/auth/login", {"login": "yanis", "password": PASSWORD})
        self.assertEqual(response.status_code, 403)

    def test_logout_ends_the_session(self):
        self.signup()
        self.assertEqual(post(self.client, "/api/auth/logout").status_code, 204)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)

    def test_writes_need_a_csrf_token(self):
        User.objects.create_user("yanis", "yanis@example.com", PASSWORD)
        client = Client(enforce_csrf_checks=True)
        credentials = {"login": "yanis", "password": PASSWORD}

        self.assertEqual(post(client, "/api/auth/login", credentials).status_code, 403)

        token = client.get("/api/auth/csrf").json()["csrf_token"]
        response = post(client, "/api/auth/login", credentials, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)

    def test_login_attempts_are_rate_limited(self):
        credentials = {"login": "personne", "password": "faux"}
        for _ in range(10):
            post(self.client, "/api/auth/login", credentials)
        self.assertEqual(post(self.client, "/api/auth/login", credentials).status_code, 429)
