import json

from django.core.cache import cache
from django.utils import timezone

from content.models import Exercise, Message, MessageFlag
from content.tests import TL, ContentTestCase, make_user
from notifications.models import Notification

from .models import Appeal, ModerationLog, Report, Sanction
from .services import create_appeal, create_report

Kind = Notification.Kind


class TeamTestCase(ContentTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        now = timezone.now()
        for user in [self.author, self.student]:
            user.email_verified_at = now
            user.save(update_fields=["email_verified_at"])
        self.mod = make_user("moderatrice", trust=TL.MODERATOR, email_verified_at=now)
        self.mod2 = make_user("moderateur2", trust=TL.MODERATOR, email_verified_at=now)
        self.admin = make_user("admin", is_staff=True, email_verified_at=now)

    def api(self, user, method, path, payload=None):
        self.client.force_login(user)
        call = getattr(self.client, method)
        if payload is None:
            return call(f"/api{path}")
        return call(f"/api{path}", json.dumps(payload), content_type="application/json")

    def message(self, author=None, body="Une question sur l'énoncé"):
        return Message.objects.create(exercise=self.exercise, author=author or self.student, body=body)


class AccessTests(TeamTestCase):
    def test_the_moderation_space_is_for_the_team_only(self):
        for path in ["/moderation/summary", "/moderation/reports", "/moderation/messages", "/moderation/appeals",
                     "/moderation/log", f"/moderation/members/{self.student.username}"]:
            self.assertEqual(self.api(self.student, "get", path).status_code, 403, path)
            self.assertEqual(self.api(self.mod, "get", path).status_code, 200, path)

    def test_the_menu_counts_what_waits_for_the_team(self):
        create_report(self.student, reason=Report.Reason.ERROR, exercise=self.exercise, details="Coquille")
        MessageFlag.objects.create(message=self.message(author=self.author), user=self.student)
        self.assertEqual(self.api(self.mod, "get", "/auth/me").json()["moderation_pending"], 2)
        self.assertEqual(self.api(self.student, "get", "/auth/me").json()["moderation_pending"], 0)


class ClaimTests(TeamTestCase):
    def test_a_colleague_sees_who_handles_a_report_until_it_is_decided(self):
        create_report(self.student, reason=Report.Reason.ERROR, exercise=self.exercise, details="Coquille")
        [group] = self.api(self.mod, "get", "/moderation/reports").json()
        self.assertIsNone(group["claim"])
        key = f"report:{group['id']}"

        taken = self.api(self.mod, "post", "/moderation/claims", {"key": key})
        self.assertEqual(taken.status_code, 200)
        self.assertTrue(taken.json()["mine"])
        [seen] = self.api(self.mod2, "get", "/moderation/reports").json()
        self.assertEqual(seen["claim"]["username"], "moderatrice")
        self.assertFalse(seen["claim"]["mine"])

        # Un collègue ne le prend pas par mégarde, mais peut prendre le relais.
        self.assertEqual(self.api(self.mod2, "post", "/moderation/claims", {"key": key}).status_code, 409)
        relay = self.api(self.mod2, "post", "/moderation/claims", {"key": key, "take_over": True})
        self.assertEqual(relay.json()["username"], "moderateur2")

        # La décision efface la prise en charge.
        path = f"/moderation/reports/{group['id']}/decide"
        self.assertEqual(self.api(self.mod2, "post", path, {"confirmed": False, "note": "Pas d'erreur."}).status_code, 204)
        from .models import ModerationClaim

        self.assertFalse(ModerationClaim.objects.exists())

    def test_a_claim_expires_and_can_be_released(self):
        from datetime import timedelta

        from .models import ModerationClaim

        flagged = self.message(author=self.author)
        MessageFlag.objects.create(message=flagged, user=self.student)
        key = f"message:{flagged.pk}"
        self.api(self.mod, "post", "/moderation/claims", {"key": key})
        ModerationClaim.objects.update(claimed_at=timezone.now() - timedelta(hours=3))
        [seen] = self.api(self.mod2, "get", "/moderation/messages").json()
        self.assertIsNone(seen["claim"])

        self.api(self.mod2, "post", "/moderation/claims", {"key": key})
        # Seul celui qui l'a pris le rend.
        self.assertEqual(self.api(self.mod, "delete", f"/moderation/claims/{key}").status_code, 204)
        self.assertTrue(ModerationClaim.objects.filter(key=key).exists())
        self.api(self.mod2, "delete", f"/moderation/claims/{key}")
        self.assertFalse(ModerationClaim.objects.exists())
        self.assertEqual(self.api(self.mod, "post", "/moderation/claims", {"key": "n'importe:1"}).status_code, 409)
        self.assertEqual(self.api(self.student, "post", "/moderation/claims", {"key": key}).status_code, 403)


class ReportQueueTests(TeamTestCase):
    def test_reports_on_one_content_are_decided_together_with_an_optional_sanction(self):
        create_report(self.student, reason=Report.Reason.PLAGIARISM, exercise=self.exercise, details="Copié d'un livre")
        create_report(self.mod2, reason=Report.Reason.PLAGIARISM, exercise=self.exercise)
        [group] = self.api(self.mod, "get", "/moderation/reports").json()
        self.assertEqual([r["username"] for r in group["reports"]], ["lea", "moderateur2"])
        self.assertEqual(group["author"]["username"], "auteur")
        self.assertIn("retiré", group["effect"])

        # Confirmer sans motif est refusé : le motif part à l'auteur.
        path = f"/moderation/reports/{group['id']}/decide"
        self.assertEqual(self.api(self.mod, "post", path, {"confirmed": True}).status_code, 409)
        response = self.api(
            self.mod, "post", path, {"confirmed": True, "note": "Recopié mot pour mot.", "sanction": "avertissement"}
        )
        self.assertEqual(response.status_code, 204)

        self.exercise.refresh_from_db()
        self.assertEqual(self.exercise.status, Exercise.Status.REMOVED)
        self.assertEqual(Report.objects.filter(status=Report.Status.CONFIRMED).count(), 2)
        self.assertTrue(Sanction.objects.filter(user=self.author, kind=Sanction.Kind.WARNING).exists())
        actions = set(ModerationLog.objects.values_list("action", flat=True))
        self.assertEqual(actions, {ModerationLog.Action.REPORT_CONFIRMED, ModerationLog.Action.SANCTION})
        self.assertEqual(self.api(self.mod, "get", "/moderation/reports").json(), [])

    def test_no_one_decides_a_report_on_their_own_content(self):
        own = self.make_exercise(author=self.mod)
        report = create_report(self.student, reason=Report.Reason.ERROR, exercise=own, details="Erreur")
        [group] = self.api(self.mod, "get", "/moderation/reports").json()
        self.assertFalse(group["can_decide"])
        path = f"/moderation/reports/{report.pk}/decide"
        self.assertEqual(self.api(self.mod, "post", path, {"confirmed": False}).status_code, 403)
        self.assertEqual(self.api(self.mod2, "post", path, {"confirmed": False}).status_code, 204)


class MessageQueueTests(TeamTestCase):
    def test_a_kept_message_leaves_the_queue_until_flagged_again(self):
        message = self.message(author=self.author)
        MessageFlag.objects.create(message=message, user=self.student)
        [item] = self.api(self.mod, "get", "/moderation/messages").json()
        self.assertEqual((item["id"], len(item["flags"]), item["kept_before"]), (message.pk, 1, False))

        self.api(self.mod, "post", f"/moderation/messages/{message.pk}/decide", {"remove": False})
        self.assertEqual(self.api(self.mod, "get", "/moderation/messages").json(), [])

        MessageFlag.objects.create(message=message, user=self.mod2)
        [item] = self.api(self.mod, "get", "/moderation/messages").json()
        self.assertTrue(item["kept_before"])
        self.assertEqual([flag["username"] for flag in item["flags"]], ["moderateur2"])

    def test_a_removed_message_can_be_appealed_and_another_moderator_decides(self):
        message = self.message(body="Voici la solution complète : ...")
        MessageFlag.objects.create(message=message, user=self.author)
        path = f"/moderation/messages/{message.pk}/decide"
        self.assertEqual(self.api(self.mod, "post", path, {"remove": True}).status_code, 409)
        self.api(self.mod, "post", path, {"remove": True, "reason": "Pas de solution dans le fil."})

        # L'auteur voit la décision, avec son motif, et fait appel.
        [decision] = self.api(self.student, "get", "/decisions/mine").json()
        self.assertEqual((decision["type"], decision["reason"], decision["can_appeal"]), ("message", "Pas de solution dans le fil.", True))
        statement = {"type": "message", "id": message.pk, "statement": "Ce n'était qu'une piste, pas la solution."}
        self.assertEqual(self.api(self.student, "post", "/appeals", statement).status_code, 201)

        [appeal] = self.api(self.mod, "get", "/moderation/appeals").json()
        self.assertEqual((appeal["decision_type"], appeal["decided_by"], appeal["can_decide"]), ("message", "moderatrice", False))
        decide = f"/moderation/appeals/{appeal['id']}/decide"
        self.assertEqual(self.api(self.mod, "post", decide, {"overturn": True, "note": "Ok"}).status_code, 403)
        self.assertEqual(
            self.api(self.mod2, "post", decide, {"overturn": True, "note": "Une piste est permise."}).status_code, 204
        )
        message.refresh_from_db()
        self.assertIsNone(message.removed_at)
        [decision] = self.api(self.student, "get", "/decisions/mine").json()
        self.assertEqual(decision["appeal_status"], Appeal.Status.OVERTURNED)


class MemberFileTests(TeamTestCase):
    def test_sanction_and_lift_from_the_member_file(self):
        path = f"/moderation/members/{self.student.username}"
        file = self.api(self.mod, "post", f"{path}/sanctions", {"kind": "suspension", "reason": "Insultes répétées."}).json()
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, "suspended")
        [sanction] = file["sanctions"]
        self.assertTrue(sanction["active"])
        # Suspendu, le membre ne peut plus écrire sous un exercice.
        response = self.api(self.student, "post", f"/exercises/{self.exercise.pk}/messages", {"body": "Bonjour"})
        self.assertEqual(response.status_code, 403)

        lifted = self.api(self.mod2, "post", f"/moderation/sanctions/{sanction['id']}/lift", {"reason": "Excuses présentées."})
        self.assertFalse(lifted.json()["sanctions"][0]["active"])
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, "active")
        self.assertEqual([entry["action"] for entry in lifted.json()["log"]], ["sanction_levee", "sanction"])

    def test_who_can_sanction_whom(self):
        self.assertFalse(self.api(self.mod, "get", f"/moderation/members/{self.mod.username}").json()["can_sanction"])
        self.assertFalse(self.api(self.mod, "get", f"/moderation/members/{self.mod2.username}").json()["can_sanction"])
        self.assertTrue(self.api(self.admin, "get", f"/moderation/members/{self.mod2.username}").json()["can_sanction"])
        response = self.api(self.mod, "post", f"/moderation/members/{self.mod2.username}/sanctions", {"kind": "avertissement", "reason": "x"})
        self.assertEqual(response.status_code, 403)

    def test_only_an_admin_names_or_removes_a_moderator(self):
        path = f"/moderation/members/{self.student.username}/moderator"
        self.assertEqual(self.api(self.mod, "post", path, {"moderator": True}).status_code, 403)
        self.assertTrue(self.api(self.admin, "post", path, {"moderator": True}).json()["is_moderator"])
        self.assertTrue(Notification.objects.filter(user=self.student, title__icontains="modération").exists())
        self.assertFalse(self.api(self.admin, "post", path, {"moderator": False}).json()["is_moderator"])
        self.student.refresh_from_db()
        self.assertLess(self.student.trust_level, TL.MODERATOR)

    def test_the_journal_lists_every_decision(self):
        report = create_report(self.student, reason=Report.Reason.ERROR, exercise=self.exercise, details="Coquille")
        self.api(self.mod, "post", f"/moderation/reports/{report.pk}/decide", {"confirmed": True, "note": "Corrigé."})
        [entry] = self.api(self.mod2, "get", "/moderation/log").json()
        self.assertEqual((entry["actor"], entry["action"], entry["member"]), ("moderatrice", "signalement_confirme", "auteur"))
        self.assertIn("Corrigé.", entry["summary"])


class AppealTests(TeamTestCase):
    def test_an_overdue_appeal_is_flagged(self):
        message = self.message()
        self.api(self.mod, "post", f"/moderation/messages/{message.pk}/decide", {"remove": True, "reason": "Hors sujet."})
        message.refresh_from_db()
        appeal = create_appeal(self.student, message, "Ce n'était pas hors sujet.")
        Appeal.objects.filter(pk=appeal.pk).update(created_at=timezone.now() - timezone.timedelta(days=8))
        self.assertEqual(self.api(self.mod2, "get", "/moderation/summary").json()["appeals_overdue"], 1)
        self.assertTrue(self.api(self.mod2, "get", "/moderation/appeals").json()[0]["overdue"])
