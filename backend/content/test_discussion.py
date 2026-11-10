import json

from django.core.cache import cache
from django.utils import timezone

from accounts.services import delete_account, export_user_data
from notifications.models import Notification

from .models import Message
from .tests import TL, ContentTestCase, make_user

Kind = Notification.Kind


class DiscussionTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        now = timezone.now()
        for user in [self.author, self.student]:
            user.email_verified_at = now
            user.save(update_fields=["email_verified_at"])
        self.team = make_user("equipe", trust=TL.MODERATOR, email_verified_at=now)
        self.url = f"/api/exercises/{self.exercise.pk}/messages"

    def post(self, user, body, parent=None):
        self.client.force_login(user)
        payload = {"body": body} if parent is None else {"body": body, "parent": parent}
        return self.client.post(self.url, json.dumps(payload), content_type="application/json")

    def thread(self):
        return self.client.get(self.url).json()

    def test_a_visitor_reads_the_thread_but_cannot_write(self):
        self.post(self.student, "Dans la question 2, $n$ est-il supposé non nul ?")
        self.client.logout()
        [message] = self.thread()
        self.assertEqual(message["author"]["username"], "lea")
        self.assertFalse(message["mine"] or message["can_remove"])
        response = self.client.post(self.url, json.dumps({"body": "Bonjour"}), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_a_question_notifies_the_author_and_a_reply_notifies_the_asker(self):
        response = self.post(self.student, "Faut-il supposer $\\alpha > 1$ ?")
        self.assertEqual(response.status_code, 201)
        question = response.json()[0]["id"]
        asked = Notification.objects.get(user=self.author, kind=Kind.DISCUSSION)
        self.assertEqual(asked.url, f"/exercices/{self.exercise.pk}#discussion")

        self.post(self.author, "Oui, c'est précisé plus haut.", parent=question)
        self.assertEqual(Notification.objects.filter(user=self.student, kind=Kind.DISCUSSION).count(), 1)
        # L'auteur ne se prévient pas lui-même.
        self.assertEqual(Notification.objects.filter(user=self.author, kind=Kind.DISCUSSION).count(), 1)

        [message] = self.thread()
        [reply] = message["replies"]
        self.assertTrue(reply["exercise_author"])
        self.assertFalse(reply["team"])

    def test_replying_to_a_reply_stays_under_the_question(self):
        question = self.post(self.student, "Une première question").json()[0]["id"]
        reply = self.post(self.author, "Une réponse", parent=question).json()[0]["replies"][0]["id"]
        self.post(self.student, "Merci !", parent=reply)
        [message] = self.thread()
        self.assertEqual([r["body"] for r in message["replies"]], ["Une réponse", "Merci !"])
        self.assertFalse(Message.objects.filter(parent__parent__isnull=False).exists())

    def test_empty_messages_forbidden_latex_and_unverified_accounts_are_refused(self):
        self.assertEqual(self.post(self.student, "   ").status_code, 422)
        self.assertEqual(self.post(self.student, r"$\def\x{1}$").status_code, 422)
        self.assertEqual(self.post(self.student, "x" * 2001).status_code, 422)
        newcomer = make_user("nouveau")
        self.assertEqual(self.post(newcomer, "Bonjour").status_code, 403)
        self.assertFalse(Message.objects.exists())

    def test_an_author_removes_their_message_and_only_theirs(self):
        question = self.post(self.student, "Ma question").json()[0]["id"]
        self.client.force_login(self.author)
        self.assertEqual(self.client.delete(f"/api/messages/{question}").status_code, 403)
        self.client.force_login(self.student)
        self.assertEqual(self.client.delete(f"/api/messages/{question}").json(), [])
        # Le texte reste en base, mais plus personne ne le lit.
        self.assertIsNotNone(Message.objects.get(pk=question).removed_at)

    def test_a_removed_question_keeps_its_place_when_it_has_replies(self):
        question = self.post(self.student, "La solution est : ...").json()[0]["id"]
        self.post(self.author, "Merci de ne pas donner la solution ici.", parent=question)
        self.client.force_login(self.team)
        # L'équipe ne retire pas le message d'un autre sans motif.
        self.assertEqual(self.client.delete(f"/api/messages/{question}").status_code, 403)
        moderate = f"/api/messages/{question}/moderate"
        self.assertEqual(
            self.client.post(moderate, json.dumps({"reason": " "}), content_type="application/json").status_code, 409
        )
        response = self.client.post(
            moderate, json.dumps({"reason": "Une solution complète n'a pas sa place ici."}), content_type="application/json"
        )
        [message] = response.json()
        self.assertTrue(message["removed"])
        self.assertEqual((message["body"], message["author"]), ("", None))
        self.assertEqual(len(message["replies"]), 1)
        # Son auteur reçoit le motif, et peut faire appel.
        removed = Notification.objects.filter(user=self.student, kind=Kind.CONTENT_REMOVED).latest("pk")
        self.assertIn("Une solution complète", removed.body)

    def test_flagging_warns_the_team_once(self):
        question = self.post(self.student, "Message hors sujet").json()[0]["id"]
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(f"/api/messages/{question}/flag").status_code, 409)
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(f"/api/messages/{question}/flag").status_code, 204)
        self.assertEqual(self.client.post(f"/api/messages/{question}/flag").status_code, 204)
        self.assertEqual(Notification.objects.filter(user=self.team, kind=Kind.DISCUSSION).count(), 1)
        self.assertTrue(self.thread()[0]["flagged"])

    def test_export_holds_the_messages_and_deletion_keeps_them_without_a_name(self):
        self.post(self.student, "Une remarque sur l'énoncé")
        self.assertEqual(export_user_data(self.student)["messages_sous_les_exercices"][0]["texte"], "Une remarque sur l'énoncé")
        delete_account(self.student)
        self.client.logout()
        [message] = self.thread()
        self.assertIsNone(message["author"])
        self.assertEqual(message["body"], "Une remarque sur l'énoncé")
