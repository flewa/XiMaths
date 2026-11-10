from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from config.errors import RuleError
from gamification.services import balance
from notifications.models import Notification

from .models import Review, Solution
from .services import alert_team, review_deadlines, revise_solution, submit_review, volunteer_review
from .tests import TL, ContentTestCase, make_user

Verdict = Review.Verdict


class ReviewFlowTestCase(ContentTestCase):
    def setUp(self):
        super().setUp()
        # Assez de relecteurs pour une réattribution ou un second tour.
        self.reviewers += [make_user(f"relecteur{i}", trust=TL.REVIEWER) for i in range(3, 7)]

    def assigned(self, solution):
        return list(solution.reviews.filter(round=solution.review_round, expired_at=None).select_related("reviewer"))


class DeadlineTests(ReviewFlowTestCase):
    def test_a_reminder_at_48_hours_then_reassignment_at_72(self):
        solution = self.publish()
        first = self.assigned(solution)[0]
        start = first.assigned_at

        self.assertEqual(review_deadlines(now=start + timedelta(hours=49)), (3, 0))
        self.assertEqual(review_deadlines(now=start + timedelta(hours=50)), (0, 0))
        self.assertTrue(Notification.objects.filter(user=first.reviewer, kind=Notification.Kind.REVIEW_REMINDER).exists())

        self.assertEqual(review_deadlines(now=start + timedelta(hours=73)), (0, 3))
        first.refresh_from_db()
        self.assertIsNotNone(first.expired_at)
        self.assertEqual(len(self.assigned(solution)), 3)
        self.assertNotIn(first.reviewer, [r.reviewer for r in self.assigned(solution)])
        with self.assertRaises(RuleError):
            submit_review(first, Verdict.CORRECT)


class VolunteerTests(ReviewFlowTestCase):
    def test_a_volunteer_review_joins_the_drawn_ones(self):
        solution = self.publish()
        volunteer = make_user("volontaire", trust=TL.REVIEWER)

        review = volunteer_review(solution, volunteer)
        status = submit_review(review, Verdict.CORRECT, feedback="Juste.")

        review.refresh_from_db()
        self.assertFalse(review.assigned)
        # Elle ne décide pas seule : les trois relectures tirées au sort restent attendues.
        self.assertEqual(status, Solution.Status.UNDER_REVIEW)
        with self.assertRaises(RuleError):
            volunteer_review(solution, volunteer)

    def test_reviewers_list_the_solutions_open_to_volunteers(self):
        solution = self.publish()
        volunteer = make_user("volontaire", trust=TL.REVIEWER, email_verified_at=timezone.now())
        self.client.force_login(volunteer)

        response = self.client.get("/api/reviews/open")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["solution_id"] for item in response.json()], [solution.pk])

    def test_members_and_the_author_cannot_volunteer(self):
        solution = self.publish()
        with self.assertRaises(PermissionDenied):
            volunteer_review(solution, make_user("membre"))
        with self.assertRaises(PermissionDenied):
            volunteer_review(solution, self.student)


class RevisionTests(ReviewFlowTestCase):
    def needs_work(self):
        solution = self.publish()
        for review in self.assigned(solution):
            submit_review(review, Verdict.INCORRECT, feedback="Étape fausse.")
        solution.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.NEEDS_WORK)
        return solution

    def test_a_revised_solution_gets_a_fresh_round_of_reviewers(self):
        solution = self.needs_work()
        previous = {r.reviewer_id for r in solution.reviews.all()}

        revised, new_round = revise_solution(solution, "Nouvelle preuve, complète cette fois : on compare à une série télescopique.")

        self.assertTrue(new_round)
        self.assertEqual((revised.status, revised.review_round), (Solution.Status.UNDER_REVIEW, 2))
        current = {r.reviewer_id for r in self.assigned(revised)}
        self.assertEqual(len(current), 3)
        self.assertFalse(current & previous)
        for review in self.assigned(revised):
            submit_review(review, Verdict.CORRECT, feedback="Juste.")
        revised.refresh_from_db()
        self.assertEqual(revised.status, Solution.Status.VALIDATED)

    def test_a_small_edit_of_a_validated_solution_stays_validated(self):
        solution = self.publish()
        for review in self.assigned(solution):
            submit_review(review, Verdict.CORRECT, feedback="Juste.")
        solution.refresh_from_db()

        _, new_round = revise_solution(solution, solution.body + " Fin.")
        self.assertFalse(new_round)
        self.assertEqual(solution.status, Solution.Status.VALIDATED)

        _, new_round = revise_solution(solution, "Une tout autre démarche, par comparaison avec une intégrale de 1/t².")
        self.assertTrue(new_round)
        self.assertEqual(solution.status, Solution.Status.UNDER_REVIEW)

    def test_only_closed_solutions_can_be_revised(self):
        with self.assertRaises(RuleError):
            revise_solution(self.publish(), "Texte assez long pour être une solution valable.")


class TeamTests(ReviewFlowTestCase):
    """Le filet : l'équipe du site voit les copies en attente, est prévenue quand l'une
    d'elles attend trop, et sa relecture vaut décision."""

    def setUp(self):
        super().setUp()
        self.team = make_user("equipe", is_staff=True, email_verified_at=timezone.now())

    def test_the_team_lists_waiting_copies_and_corrects_one(self):
        solution = self.publish()
        self.client.force_login(self.team)

        [item] = self.client.get("/api/reviews/open").json()
        self.assertEqual((item["solution_id"], item["reviews_done"], item["reviews_expected"]), (solution.pk, 0, 3))

        task = self.client.post(f"/api/solutions/{solution.pk}/volunteer").json()
        self.assertEqual(task["solution_id"], solution.pk)
        result = self.client.post(
            f"/api/reviews/{task['id']}",
            {"verdict": "correcte", "feedback": "Preuve juste et bien rédigée."},
            content_type="application/json",
        )
        self.assertEqual(result.json()["solution_status"], "validated")
        self.assertEqual(self.client.get("/api/reviews/open").json(), [])

    def test_the_team_is_alerted_once_a_day_about_copies_waiting_three_days(self):
        solution = self.publish()
        sent = solution.updated_at
        kind = Notification.Kind.TEAM_ALERT

        self.assertEqual(alert_team(now=sent + timedelta(hours=71)), 0)
        self.assertEqual(alert_team(now=sent + timedelta(hours=73)), 1)
        alert = Notification.objects.get(user=self.team, kind=kind)
        self.assertIn("Une copie attend", alert.title)
        # Par email aussi : envoyé aussitôt, ou retenu jusqu'à 8 h pendant les heures calmes.
        self.assertTrue(alert.email_pending or alert.emailed_at)
        # L'alerte porte l'heure réelle : on la date de l'heure simulée, pour la suite.
        Notification.objects.filter(pk=alert.pk).update(created_at=sent + timedelta(hours=73))
        # Pas deux fois dans la journée ; de nouveau le lendemain, tant qu'elle attend.
        self.assertEqual(alert_team(now=sent + timedelta(hours=80)), 0)
        self.assertEqual(alert_team(now=sent + timedelta(hours=97)), 1)
        # Une copie corrigée n'alerte plus personne.
        submit_review(volunteer_review(solution, self.team), Verdict.CORRECT, feedback="Juste.")
        self.assertEqual(alert_team(now=sent + timedelta(hours=130)), 0)
        self.assertFalse(Notification.objects.filter(kind=kind).exclude(user=self.team).exists())
