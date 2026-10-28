from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

from django.core import mail
from django.utils import timezone

from content.tests import ContentTestCase, make_user

from .models import Notification
from .services import notify, purge_old, send_digests, send_pending_emails

Kind = Notification.Kind


def paris(*args):
    return timezone.make_aware(datetime(*args))


class NotifyTests(ContentTestCase):
    def test_important_events_are_emailed_outside_quiet_hours(self):
        notify(self.student, Kind.CONTENT_REMOVED, "Retrait", "Motif : copie.", "/decisions", now=paris(2026, 10, 28, 14))
        [message] = mail.outbox
        self.assertEqual(message.subject, "Retrait")
        self.assertIn("List-Unsubscribe", message.extra_headers)

    def test_quiet_hours_hold_the_email_until_8(self):
        notify(self.student, Kind.SANCTION, "Décision", now=paris(2026, 10, 28, 23))
        self.assertEqual(mail.outbox, [])
        self.assertEqual(send_pending_emails(now=paris(2026, 10, 29, 7)), 0)
        self.assertEqual(send_pending_emails(now=paris(2026, 10, 29, 8, 5)), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_routine_events_stay_in_the_app_and_opt_out_is_respected(self):
        notify(self.student, Kind.BADGE, "Badge", now=paris(2026, 10, 28, 14))
        self.student.email_notifications = False
        notify(self.student, Kind.CONTENT_REMOVED, "Retrait", now=paris(2026, 10, 28, 14))
        self.assertEqual(mail.outbox, [])
        self.assertEqual(Notification.objects.filter(user=self.student).count(), 2)

    def test_review_assignment_and_validation_are_notified(self):
        solution = self.publish()
        reviewers = set(solution.reviews.values_list("reviewer_id", flat=True))
        self.assertEqual(
            set(Notification.objects.filter(kind=Kind.REVIEW_ASSIGNED).values_list("user_id", flat=True)), reviewers
        )
        for reviewer in self.reviewers[:2]:
            self.review(solution, reviewer, "correcte")
        self.assertTrue(Notification.objects.filter(user=self.student, kind=Kind.SOLUTION_VALIDATED).exists())
        self.assertTrue(Notification.objects.filter(user=self.author, kind=Kind.EXERCISE_SOLVED).exists())


class DigestTests(ContentTestCase):
    def test_one_digest_per_week_and_one_click_unsubscribe(self):
        self.student.weekly_digest = True
        self.student.save()
        notify(self.student, Kind.BADGE, "Nouveau badge : Premier pas", url="/badges")

        self.assertEqual(send_digests(), 1)
        self.assertEqual(send_digests(), 0)
        link = mail.outbox[-1].extra_headers["List-Unsubscribe"].strip("<>")
        token = parse_qs(urlparse(link).query)["token"][0]

        response = self.client.get("/api/notifications/unsubscribe", {"token": token})

        self.assertEqual(response["Location"], "http://localhost:3000/desabonnement?ok=1")
        self.student.refresh_from_db()
        self.assertEqual((self.student.weekly_digest, self.student.email_notifications), (False, False))

    def test_notifications_are_kept_six_months(self):
        old = notify(self.student, Kind.BADGE, "Ancien")
        Notification.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=200))
        notify(self.student, Kind.BADGE, "Récent")
        self.assertEqual(purge_old(), 1)


class NotificationApiTests(ContentTestCase):
    def test_list_and_mark_as_read(self):
        notify(self.student, Kind.BADGE, "Un")
        second = notify(self.student, Kind.BADGE, "Deux")
        notify(make_user("autre"), Kind.BADGE, "Pas pour toi")
        self.client.force_login(self.student)

        data = self.client.get("/api/notifications").json()
        self.assertEqual((data["unread"], [n["title"] for n in data["items"]]), (2, ["Deux", "Un"]))
        self.client.post(f"/api/notifications/{second.pk}/read")
        self.assertEqual(self.client.get("/api/auth/me").json()["unread_notifications"], 1)
        self.client.post("/api/notifications/read")
        self.assertEqual(self.client.get("/api/notifications").json()["unread"], 0)
