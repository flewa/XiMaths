import base64
import json
import os
from datetime import datetime, time, timedelta
from io import StringIO
from unittest import mock

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from accounts.services import delete_account, export_user_data
from accounts.tests import post
from content.tests import ContentTestCase, make_user

from . import push
from .models import Notification, PushSubscription
from .services import notify

Kind = Notification.Kind
ENDPOINT = "https://fcm.googleapis.com/fcm/send/abc123"


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def vapid_keys():
    out = StringIO()
    call_command("generate_vapid_keys", stdout=out)
    return dict(line.split("=", 1) for line in out.getvalue().splitlines())


KEYS = vapid_keys()


def browser_keys():
    """Les clés d'un abonnement, telles qu'un navigateur les crée."""
    private = ec.generate_private_key(ec.SECP256R1())
    public = private.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    return {"p256dh": b64url(public), "auth": b64url(os.urandom(16))}


def today_at(hour):
    return timezone.make_aware(datetime.combine(timezone.localdate(), time(hour)))


class Sent:
    """Remplace l'envoi HTTP de pywebpush : le chiffrement et la signature VAPID restent réels."""

    def __init__(self, status=201):
        self.status = status
        self.calls = []

    def __call__(self, url, data=None, headers=None, timeout=None):
        self.calls.append({"url": url, "data": data, "headers": headers})
        return mock.Mock(status_code=self.status, reason="", text="")


@override_settings(VAPID_PUBLIC_KEY=KEYS["VAPID_PUBLIC_KEY"], VAPID_PRIVATE_KEY=KEYS["VAPID_PRIVATE_KEY"])
class PushTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.device = PushSubscription.objects.create(user=self.student, endpoint=ENDPOINT, **browser_keys())

    def send(self, *, at, status=201):
        sent = Sent(status)
        with mock.patch("pywebpush.requests.post", sent):
            reached = push.deliver(self.student, now=at)
        return reached, sent.calls

    def note(self, kind=Kind.SOLUTION_VALIDATED, title="Solution validée"):
        return Notification.objects.create(user=self.student, kind=kind, title=title, body="Bravo.", url="/exercices/1")

    def test_a_push_is_encrypted_signed_and_sent_once_a_day(self):
        self.note()

        reached, calls = self.send(at=today_at(12))

        self.assertEqual(reached, 1)
        [call] = calls
        self.assertEqual(call["url"], ENDPOINT)
        self.assertEqual(call["headers"]["content-encoding"], "aes128gcm")
        self.assertTrue(call["headers"]["authorization"].startswith("vapid t="))
        self.assertNotIn(b"Bravo", call["data"])  # chiffré
        self.assertEqual(Notification.objects.get().pushed_at, today_at(12))

        self.note(title="Une autre")
        self.assertEqual(self.send(at=today_at(18)), (0, []))

    def test_quiet_hours_hold_the_push_and_8_am_sends_one_summary(self):
        self.note(title="Solution validée")
        self.note(Kind.REVIEW_ASSIGNED, "Relecture attribuée")
        night = today_at(23)
        payloads = []
        original = push._payload

        def recorded(pending):
            payloads.append(json.loads(original(pending)))
            return original(pending)

        self.assertEqual(self.send(at=night), (0, []))
        with mock.patch.object(push, "_payload", side_effect=recorded):
            reached, _ = self.send(at=night + timedelta(hours=9))

        self.assertEqual(reached, 1)
        self.assertEqual(payloads[0]["title"], "2 nouveautés sur XiMaths")
        self.assertEqual(payloads[0]["url"], "/notifications")
        self.assertEqual(Notification.objects.filter(pushed_at=None).count(), 0)

    def test_routine_read_and_old_notifications_are_not_pushed(self):
        self.note(Kind.BADGE, "Badge")
        read = self.note()
        read.read_at = timezone.now()
        read.save()

        self.assertEqual(self.send(at=today_at(12)), (0, []))
        self.assertEqual(self.send(at=today_at(12) + timedelta(days=2)), (0, []))

    def test_an_expired_subscription_is_removed(self):
        self.note()

        reached, _ = self.send(at=today_at(12), status=410)

        self.assertEqual(reached, 0)
        self.assertFalse(PushSubscription.objects.exists())
        self.assertIsNone(Notification.objects.get().pushed_at)

    def test_a_failed_send_is_retried_by_the_hourly_job(self):
        self.note()
        self.send(at=today_at(12), status=500)

        sent = Sent()
        with mock.patch("pywebpush.requests.post", sent):
            self.assertEqual(push.send_pending_pushes(now=today_at(13)), 1)
        self.assertEqual(len(sent.calls), 1)

    def test_notify_pushes_after_commit(self):
        sent = Sent()
        with mock.patch("pywebpush.requests.post", sent), self.captureOnCommitCallbacks(execute=True):
            notify(self.student, Kind.SOLUTION_VALIDATED, "Solution validée", now=today_at(12))
            notify(self.student, Kind.BADGE, "Badge", now=today_at(12))

        self.assertEqual(len(sent.calls), 1)

    @override_settings(VAPID_PRIVATE_KEY="")
    def test_nothing_is_sent_without_keys(self):
        self.note()
        self.assertEqual(self.send(at=today_at(12)), (0, []))


@override_settings(VAPID_PUBLIC_KEY=KEYS["VAPID_PUBLIC_KEY"], VAPID_PRIVATE_KEY=KEYS["VAPID_PRIVATE_KEY"])
class PushApiTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.client.force_login(self.student)

    def subscribe(self, endpoint=ENDPOINT):
        return post(self.client, "/api/push/subscriptions", {"endpoint": endpoint, "keys": browser_keys()})

    def test_the_key_then_subscribe_and_unsubscribe(self):
        self.assertEqual(self.client.get("/api/push/key").json(), {"public_key": KEYS["VAPID_PUBLIC_KEY"]})

        self.assertEqual(self.subscribe().status_code, 204)
        self.assertEqual(self.subscribe().status_code, 204)  # même navigateur : mis à jour
        self.assertEqual(PushSubscription.objects.filter(user=self.student).count(), 1)

        post(self.client, "/api/push/unsubscribe", {"endpoint": ENDPOINT})
        self.assertFalse(PushSubscription.objects.exists())

    def test_only_browser_push_services_are_accepted(self):
        for endpoint in (
            "https://127.0.0.1/interne",
            "http://fcm.googleapis.com/fcm/send/x",
            "https://fcm.googleapis.com.example.com/x",
            "https://fcm.googleapis.com:8443/x",
        ):
            self.assertEqual(self.subscribe(endpoint).status_code, 422, endpoint)
        for endpoint in (
            "https://updates.push.services.mozilla.com/wpush/v2/x",
            "https://web.push.apple.com/x",
            "https://wns2-par02p.notify.windows.com/w/?token=x",
        ):
            self.assertEqual(self.subscribe(endpoint).status_code, 204, endpoint)

    def test_malformed_keys_are_refused(self):
        for keys in ({"p256dh": "abc", "auth": browser_keys()["auth"]}, {"p256dh": browser_keys()["p256dh"], "auth": "!!"}):
            response = post(self.client, "/api/push/subscriptions", {"endpoint": ENDPOINT, "keys": keys})
            self.assertEqual(response.status_code, 422)

    def status(self):
        return post(self.client, "/api/push/status", {"endpoint": ENDPOINT}).json()["active"]

    def test_a_browser_changing_account_changes_owner_and_devices_are_capped(self):
        self.subscribe()
        self.client.force_login(self.author)
        self.assertFalse(self.status())  # abonné, mais pour le compte de lea
        self.subscribe()
        self.assertTrue(self.status())
        self.assertEqual(PushSubscription.objects.get().user, self.author)

        for n in range(push.MAX_DEVICES + 2):
            self.subscribe(f"{ENDPOINT}/{n}")
        self.assertEqual(PushSubscription.objects.filter(user=self.author).count(), push.MAX_DEVICES)

    @override_settings(VAPID_PUBLIC_KEY="", VAPID_PRIVATE_KEY="")
    def test_without_keys_the_setting_is_hidden(self):
        self.assertEqual(self.client.get("/api/push/key").json(), {"public_key": None})
        self.assertEqual(self.subscribe().status_code, 404)

    def test_export_and_deletion(self):
        self.subscribe()
        [device] = export_user_data(self.student)["appareils_notifications_push"]
        self.assertEqual(device["service"], "fcm.googleapis.com")

        delete_account(self.student)
        self.assertFalse(PushSubscription.objects.exists())

    def test_subscribing_needs_a_session(self):
        self.client.logout()
        self.assertEqual(self.subscribe().status_code, 401)
        self.assertEqual(make_user("x").push_subscriptions.count(), 0)
