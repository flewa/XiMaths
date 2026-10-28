import random
from unittest import mock

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from config.errors import RuleError
from content.models import Solution
from content.tests import ContentTestCase, make_user
from gamification.services import balance
from notifications.models import Notification

from .models import IntegritySignal
from .services import decide_signal

LONG_PROOF = (
    "Supposons que $\\sqrt{2} = p/q$ avec $p$ et $q$ entiers premiers entre eux. Alors $p^2 = 2q^2$, "
    "donc $p^2$ est pair et $p$ aussi : écrivons $p = 2k$. Il vient $4k^2 = 2q^2$, soit $q^2 = 2k^2$, "
    "donc $q$ est pair. Les deux entiers sont pairs, ce qui contredit leur primalité relative. "
    "Ainsi $\\sqrt{2}$ n'est pas rationnel, et la démonstration par l'absurde est complète. "
    "On remarque que le même argument s'applique à la racine de tout nombre premier, en remplaçant "
    "la parité par la divisibilité par ce nombre premier dans chacune des étapes précédentes."
)
OTHER_PROOF = (
    "On compare la série à une intégrale : la fonction $t \\mapsto 1/t^2$ est décroissante sur "
    "$[1, +\\infty[$, donc $\\sum_{n \\geq 2} 1/n^2 \\leq \\int_1^{+\\infty} dt/t^2 = 1$."
)


class IntegrityTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.moderator = make_user("modo", is_staff=True)

    def propose(self, author, body):
        solution = Solution.objects.create(exercise=self.exercise, author=author, body=body)
        from content.services import publish_solution

        return publish_solution(solution, rng=random.Random(0))

    def test_a_copied_solution_is_held_with_a_neutral_question(self):
        self.propose(self.student, LONG_PROOF)
        copier = make_user("copieur")

        copy = self.propose(copier, LONG_PROOF.replace("Supposons", "Admettons"))

        self.assertEqual(copy.status, Solution.Status.HELD)
        self.assertFalse(copy.reviews.exists())
        signal = IntegritySignal.objects.get(solution=copy)
        self.assertGreaterEqual(signal.value, 0.7)
        self.assertTrue(Notification.objects.filter(user=copier, kind=Notification.Kind.SOLUTION_HELD).exists())
        self.assertEqual(balance(copier), 2)  # l'effort reste payé tant que rien n'est confirmé

    def test_different_proofs_and_the_same_author_are_not_flagged(self):
        self.propose(self.student, LONG_PROOF)
        other = self.propose(make_user("autre"), OTHER_PROOF)
        self.assertEqual(other.status, Solution.Status.UNDER_REVIEW)
        self.assertFalse(IntegritySignal.objects.exists())

    def test_short_proofs_need_a_higher_similarity(self):
        self.propose(self.student, LONG_PROOF)
        with mock.patch("moderation.integrity.similarity", return_value=0.75):
            long_copy = self.propose(make_user("long"), LONG_PROOF + " Fin.")
            short = self.propose(make_user("court"), "Par l'absurde : p et q seraient pairs tous les deux.")
        self.assertEqual((long_copy.status, short.status), (Solution.Status.HELD, Solution.Status.UNDER_REVIEW))

    def test_clearing_sends_the_solution_to_review(self):
        self.propose(self.student, LONG_PROOF)
        copy = self.propose(make_user("copieur"), LONG_PROOF)
        signal = IntegritySignal.objects.get(solution=copy)
        with self.assertRaises(PermissionDenied):
            decide_signal(signal, confirmed=False, moderator=self.student)

        decide_signal(signal, confirmed=False, moderator=self.moderator)

        copy.refresh_from_db()
        self.assertEqual(copy.status, Solution.Status.UNDER_REVIEW)
        self.assertTrue(copy.reviews.exists())

    def test_confirmed_plagiarism_hides_and_penalizes_with_a_motive(self):
        self.propose(self.student, LONG_PROOF)
        copier = make_user("copieur")
        copy = self.propose(copier, LONG_PROOF)
        signal = IntegritySignal.objects.get(solution=copy)
        with self.assertRaises(RuleError):
            decide_signal(signal, confirmed=True, moderator=self.moderator, note=" ")

        decide_signal(signal, confirmed=True, moderator=self.moderator, note="Copie mot pour mot.")

        copy.refresh_from_db()
        self.assertEqual(copy.status, Solution.Status.HIDDEN)
        self.assertEqual(balance(copier), -50)
        removal = Notification.objects.get(user=copier, kind=Notification.Kind.CONTENT_REMOVED)
        self.assertIn("Copie mot pour mot.", removal.body)

    def test_the_author_sees_the_question_and_answers_it(self):
        self.propose(self.student, LONG_PROOF)
        copier = make_user("copieur", email_verified_at=timezone.now())
        copy = self.propose(copier, LONG_PROOF)
        signal = IntegritySignal.objects.get(solution=copy)
        self.client.force_login(copier)

        [mine] = self.client.get(f"/api/exercises/{self.exercise.pk}/my-solutions").json()
        self.assertEqual((mine["status"], mine["integrity_signal_id"]), ("held", signal.pk))
        self.assertIn("sans a priori", mine["integrity_question"])

        response = self.client.post(
            f"/api/integrity/{signal.pk}/answer",
            {"answer": "J'ai suivi le cours de mon professeur."},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 204)
        signal.refresh_from_db()
        self.assertEqual(signal.author_answer, "J'ai suivi le cours de mon professeur.")

        self.client.force_login(self.student)
        other = self.client.post(f"/api/integrity/{signal.pk}/answer", {"answer": "Moi aussi."}, content_type="application/json")
        self.assertEqual(other.status_code, 404)
