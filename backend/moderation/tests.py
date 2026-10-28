from django.core.exceptions import PermissionDenied
from django.utils import timezone

from accounts.links import check_vote_reciprocity, link_accounts
from accounts.models import AccountLink
from catalog.models import Level
from config.errors import RuleError
from content.feed import compute_scores
from content.models import Exercise, Review, Solution, Vote
from content.services import cast_vote, eligible_reviewers, publish_exercise
from content.tests import ContentTestCase, make_user
from duplicates.models import DuplicatePair
from duplicates.services import decide, index_exercise
from gamification.models import UserBadge
from gamification.services import balance

from .models import Report
from .services import create_report, resolve_report

Reason = Report.Reason
Status = Report.Status


class ModerationTestCase(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.moderator = make_user("modo", is_staff=True)
        self.witness = make_user("temoin")

    def validated_solution(self, author=None):
        solution = self.publish(author=author)
        for reviewer in self.reviewers[:2]:
            self.review(solution, reviewer, Review.Verdict.CORRECT)
        return solution

    def exercise_by(self, author, statement="Montrer que $\\sqrt{2}$ est irrationnel.", title="Exercice"):
        exercise = Exercise.objects.create(
            author=author,
            title=title,
            statement=statement,
            difficulty_declared=2,
            primary_level=Level.objects.get(code="L1"),
        )
        return publish_exercise(exercise)


class ReportTests(ModerationTestCase):
    def test_confirmed_plagiarism_hides_the_solution_and_rewards_every_reporter(self):
        solution = self.validated_solution()
        self.assertGreater(balance(self.student), 0)
        first = create_report(self.witness, reason=Reason.PLAGIARISM, solution=solution, details="Copié du livre X.")
        second = create_report(make_user("autre"), reason=Reason.PLAGIARISM, solution=solution)

        resolve_report(first, confirmed=True, moderator=self.moderator, note="Copie de la page 12 du livre X.")

        solution.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(solution.status, Solution.Status.HIDDEN)
        self.assertEqual(balance(self.student), -50)
        self.assertEqual(second.status, Status.CONFIRMED)
        self.assertEqual(balance(self.witness), 3)
        self.assertEqual(balance(second.reporter), 3)

    def test_an_inappropriate_exercise_is_removed_and_its_points_reversed(self):
        report = create_report(self.witness, reason=Reason.INAPPROPRIATE, exercise=self.exercise)
        self.assertEqual(balance(self.author), 5)

        resolve_report(report, confirmed=True, moderator=self.moderator, note="Propos injurieux.")

        self.exercise.refresh_from_db()
        self.assertEqual(self.exercise.status, Exercise.Status.REMOVED)
        self.assertEqual(balance(self.author), 0)
        self.assertEqual(balance(self.witness), 0)  # pas de points pour ce motif
        self.assertEqual(self.client.get(f"/api/exercises/{self.exercise.pk}").status_code, 404)

    def test_undeclared_ai_cancels_points_without_a_public_label(self):
        solution = self.validated_solution()
        report = create_report(self.witness, reason=Reason.UNDECLARED_AI, solution=solution)

        resolve_report(report, confirmed=True, moderator=self.moderator, note="Aveu de l'auteur.")

        solution.refresh_from_db()
        self.assertEqual((solution.status, solution.ai_usage), (Solution.Status.VALIDATED, "aucune"))
        self.assertEqual(balance(self.student), 0)

    def test_an_error_report_changes_nothing_by_itself_but_rewards_the_reporter(self):
        report = create_report(self.witness, reason=Reason.ERROR, exercise=self.exercise)
        resolve_report(report, confirmed=True, moderator=self.moderator, note="Hypothèse manquante, corrigée.")
        self.exercise.refresh_from_db()
        self.assertEqual(self.exercise.status, Exercise.Status.PUBLISHED)
        self.assertEqual(balance(self.witness), 3)

    def test_a_rejected_report_earns_nothing(self):
        report = create_report(self.witness, reason=Reason.ERROR, exercise=self.exercise)
        resolve_report(report, confirmed=False, moderator=self.moderator)
        self.assertEqual((report.status, balance(self.witness)), (Status.REJECTED, 0))

    def test_decisions_are_human_and_motivated(self):
        report = create_report(self.witness, reason=Reason.ERROR, exercise=self.exercise)
        with self.assertRaises(PermissionDenied):
            resolve_report(report, confirmed=True, moderator=self.reviewers[0], note="Oui.")
        with self.assertRaises(RuleError):
            resolve_report(report, confirmed=True, moderator=self.moderator, note="  ")
        resolve_report(report, confirmed=False, moderator=self.moderator)
        with self.assertRaises(RuleError):
            resolve_report(report, confirmed=True, moderator=self.moderator, note="Finalement oui.")

    def test_reporting_rules(self):
        with self.assertRaises(PermissionDenied):
            create_report(self.author, reason=Reason.ERROR, exercise=self.exercise)
        with self.assertRaises(RuleError):
            create_report(self.witness, reason=Reason.UNDECLARED_AI, exercise=self.exercise)
        create_report(self.witness, reason=Reason.ERROR, exercise=self.exercise)
        with self.assertRaises(RuleError):
            create_report(self.witness, reason=Reason.ERROR, exercise=self.exercise)

    def test_an_open_report_halves_the_exercise_in_the_feed(self):
        self.validated_solution()
        before = compute_scores([self.exercise])[self.exercise.pk].trending
        create_report(self.witness, reason=Reason.ERROR, exercise=self.exercise)
        after = compute_scores([self.exercise])[self.exercise.pk].trending
        self.assertAlmostEqual(after, before / 2)


class DuplicateReportTests(ModerationTestCase):
    def setUp(self):
        super().setUp()
        self.original = self.exercise_by(self.author, title="Original")
        self.copy = self.exercise_by(self.student, title="Copie")
        self.hunter = self.reviewers[0]

    def report(self, reporter=None):
        return create_report(
            reporter or self.hunter, reason=Reason.DUPLICATE, exercise=self.copy, duplicate_of=self.original
        )

    def test_only_reviewers_report_duplicates(self):
        with self.assertRaises(PermissionDenied):
            self.report(self.witness)

    def test_a_duplicate_report_joins_the_queue_and_follows_its_decision(self):
        for exercise in (self.original, self.copy):
            index_exercise(exercise)
        report = self.report()
        pair = report.duplicate_pair
        self.assertEqual(
            (pair.exercise, pair.existing, pair.band, pair.jaccard),
            (self.copy, self.original, DuplicatePair.Band.REPORTED, 1.0),
        )

        decide(pair, DuplicatePair.Status.MERGED, self.moderator)

        report.refresh_from_db()
        self.assertEqual(report.status, Status.CONFIRMED)
        self.assertEqual(balance(self.hunter), 3)
        self.assertTrue(UserBadge.objects.filter(user=self.hunter, badge="chasseur-de-doublons").exists())
        with self.assertRaises(RuleError):
            resolve_report(report, confirmed=False, moderator=self.moderator)

    def test_a_distinct_decision_rejects_the_report_and_closes_the_pair_for_good(self):
        report = self.report()
        decide(report.duplicate_pair, DuplicatePair.Status.DISTINCT, self.moderator)
        report.refresh_from_db()
        self.assertEqual((report.status, balance(self.hunter)), (Status.REJECTED, 0))
        with self.assertRaises(RuleError):
            self.report(self.reviewers[1])

    def test_reports_on_a_pending_pair_join_it(self):
        first = self.report()
        second = self.report(self.reviewers[1])
        self.assertEqual(first.duplicate_pair, second.duplicate_pair)
        self.assertEqual(DuplicatePair.objects.count(), 1)


class ReportApiTests(ModerationTestCase):
    def setUp(self):
        super().setUp()
        self.witness.email_verified_at = timezone.now()
        self.witness.save()

    def post(self, data):
        return self.client.post("/api/reports", data, content_type="application/json")

    def test_report_then_follow_it(self):
        self.assertEqual(self.post({"target": "exercise", "target_id": self.exercise.pk, "reason": "erreur"}).status_code, 401)
        self.client.force_login(self.witness)

        response = self.post(
            {"target": "exercise", "target_id": self.exercise.pk, "reason": "erreur", "details": "n = 0 ?"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status_label"], "À traiter")
        resolve_report(Report.objects.get(), confirmed=False, moderator=self.moderator)

        [mine] = self.client.get("/api/reports/mine").json()
        self.assertEqual((mine["status"], mine["title"]), ("rejete", self.exercise.title))
        self.assertNotIn("decision_note", mine)

    def test_bad_reports_are_refused(self):
        self.client.force_login(self.witness)
        unknown = self.post(
            {"target": "exercise", "target_id": self.exercise.pk, "reason": "doublon", "duplicate_of": 999}
        )
        self.assertEqual(unknown.status_code, 422)

        self.client.force_login(self.author)
        own = self.post({"target": "exercise", "target_id": self.exercise.pk, "reason": "erreur"})
        self.assertEqual(own.status_code, 403)

    def test_the_admin_confirms_with_a_motive(self):
        report = create_report(self.witness, reason=Reason.INAPPROPRIATE, exercise=self.exercise)
        self.client.force_login(make_user("admin", is_staff=True, is_superuser=True))
        url = f"/admin/moderation/report/{report.pk}/change/"

        missing = self.client.post(url, {"decision": "confirme", "motif": ""})
        self.assertContains(missing, "Motive la décision")

        self.client.post(url, {"decision": "confirme", "motif": "Contenu hors sujet et injurieux."})
        report.refresh_from_db()
        self.exercise.refresh_from_db()
        self.assertEqual((report.status, self.exercise.status), (Status.CONFIRMED, Exercise.Status.REMOVED))


class AccountLinkTests(ModerationTestCase):
    def exercises_by(self, author, count):
        return [self.exercise_by(author, title=f"{author.username} {i}") for i in range(count)]

    def test_reciprocal_voting_links_the_accounts_and_neutralizes_their_votes(self):
        alice, bob = make_user("alice"), make_user("bob")
        for exercise in self.exercises_by(bob, 10):
            cast_vote(alice, exercise=exercise)
        for exercise in self.exercises_by(alice, 9):
            cast_vote(bob, exercise=exercise)
        self.assertFalse(AccountLink.objects.exists())  # 9 votes de bob : sous le seuil

        cast_vote(bob, exercise=self.exercise_by(alice, title="dernier"))

        link = AccountLink.objects.get()
        self.assertEqual((link.link_type, link.strength), (AccountLink.LinkType.VOTE_RECIPROCITY, 1.0))
        self.assertFalse(Vote.objects.exclude(weight=0).exists())
        # Il ne leur reste que les points de publication.
        self.assertEqual((balance(alice), balance(bob)), (5 * 3, 5 * 3))

    def test_linked_accounts_do_not_review_or_promote_each_other(self):
        link_accounts(self.student, self.reviewers[0], AccountLink.LinkType.SAME_DEVICE, confirmed_by=self.moderator)
        solution = self.publish()
        self.assertNotIn(self.reviewers[0], eligible_reviewers(solution))

        exercise = self.exercise_by(self.student)
        Solution.objects.create(
            exercise=exercise, author=self.reviewers[0], body=".", status=Solution.Status.VALIDATED
        )
        self.assertEqual(compute_scores([exercise])[exercise.pk].popular, 0)
        self.assertEqual(cast_vote(self.reviewers[0], exercise=exercise).weight, 0)

    def test_a_one_sided_fan_is_not_linked(self):
        alice, bob = make_user("alice"), make_user("bob")
        for exercise in self.exercises_by(bob, 12):
            cast_vote(alice, exercise=exercise)
        self.assertIsNone(check_vote_reciprocity(alice, bob))
        self.assertFalse(AccountLink.objects.exists())
