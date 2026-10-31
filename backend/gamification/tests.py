from datetime import UTC, datetime, timedelta
from io import StringIO
from itertools import count

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from catalog.models import Level, Topic
from content.models import Exercise, Review, Solution, Vote
from content.tests import ContentTestCase, make_user

from .badges import check_badges
from .models import PointTransaction, UserBadge
from .rankings import Week, neighbourhood, standings
from .scoring import validated_solution_points
from .services import apply_plagiarism, award, balance, reverse

Reason = PointTransaction.Reason
User = get_user_model()
TL = User.TrustLevel


def paris(*args):
    return timezone.make_aware(datetime(*args))


class LedgerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("lea", "lea@example.com")
        self.level = Level.objects.get(code="L1")

    def make_exercise(self, **fields):
        fields = {
            "author": self.user,
            "title": "Exercice",
            "statement": "Montrer que $\\sqrt{2}$ est irrationnel.",
            "difficulty_declared": 2,
            "primary_level": self.level,
            **fields,
        }
        return Exercise.objects.create(**fields)

    def make_solution(self, exercise, author):
        return Solution.objects.create(exercise=exercise, author=author, body="Preuve.")

    def test_award_is_idempotent_per_source(self):
        exercise = self.make_exercise()
        first = award(self.user, Reason.EXERCISE_PUBLISHED, exercise)
        second = award(self.user, Reason.EXERCISE_PUBLISHED, exercise)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(balance(self.user), 5)

    def test_ledger_rows_cannot_be_edited_or_deleted(self):
        txn = award(self.user, Reason.EXERCISE_PUBLISHED, self.make_exercise())
        txn.amount = 100
        with self.assertRaises(ValueError):
            txn.save()
        with self.assertRaises(ValueError):
            txn.delete()

    def test_reverse_cancels_once(self):
        txn = award(self.user, Reason.EXERCISE_PUBLISHED, self.make_exercise())
        first = reverse(txn)
        second = reverse(txn)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(balance(self.user), 0)
        with self.assertRaises(ValueError):
            reverse(first)

    def test_only_three_published_exercises_pay_per_day(self):
        rewarded = [
            award(self.user, Reason.EXERCISE_PUBLISHED, self.make_exercise()) is not None
            for _ in range(4)
        ]
        self.assertEqual(rewarded, [True, True, True, False])
        self.assertEqual(balance(self.user), 15)

    def test_daily_cap_resets_the_next_day(self):
        now = timezone.now()
        for _ in range(3):
            award(self.user, Reason.EXERCISE_PUBLISHED, self.make_exercise(), now=now)
        exercise = self.make_exercise()
        self.assertIsNone(award(self.user, Reason.EXERCISE_PUBLISHED, exercise, now=now))
        tomorrow = now + timedelta(days=1)
        self.assertIsNotNone(
            award(self.user, Reason.EXERCISE_PUBLISHED, exercise, now=tomorrow)
        )

    def test_unvalidated_actions_share_a_40_point_daily_cap(self):
        exercise = self.make_exercise()
        for _ in range(3):
            award(self.user, Reason.EXERCISE_PUBLISHED, self.make_exercise())
        for _ in range(5):
            award(self.user, Reason.SOLUTION_ATTEMPT, self.make_solution(exercise, self.user))
        for _ in range(15):
            award(self.user, Reason.REVIEW_AGREED, self.make_solution(exercise, self.user))
        self.assertEqual(balance(self.user), 40)

    def test_validated_points_follow_difficulty_and_ai_usage(self):
        cases = {
            (1, "aucune"): 15,
            (2, "aucune"): 19,
            (3, "aucune"): 23,
            (5, "aucune"): 38,
            (3, "relecture"): 23,
            (3, "aide_idee"): 11,
            (5, "generee"): 0,
        }
        for (difficulty, ai_usage), expected in cases.items():
            with self.subTest(difficulty=difficulty, ai_usage=ai_usage):
                self.assertEqual(validated_solution_points(difficulty, ai_usage), expected)

    def test_plagiarism_reverses_points_from_the_solution_and_penalizes(self):
        copier = User.objects.create_user("copieur", "copieur@example.com")
        exercise = self.make_exercise()
        solution = self.make_solution(exercise, copier)
        award(copier, Reason.SOLUTION_ATTEMPT, solution)
        award(copier, Reason.SOLUTION_VALIDATED, solution, amount=19)
        award(self.user, Reason.EXERCISE_SOLVED, solution)

        apply_plagiarism(solution)

        self.assertEqual(balance(copier), -50)
        self.assertEqual(balance(self.user), 0)


class WeekTests(SimpleTestCase):
    def test_a_week_runs_from_monday_to_monday_in_paris_time(self):
        week = Week.parse("2026-W44")
        self.assertEqual(week.start, paris(2026, 10, 26))
        self.assertEqual(week.end, paris(2026, 11, 2))
        self.assertEqual(week.start.utcoffset(), timedelta(hours=1))

    def test_the_week_of_the_daylight_saving_change_lasts_167_hours(self):
        week = Week.parse("2026-W13")
        # En UTC : entre deux dates du même fuseau, Python soustrait les heures locales.
        elapsed = week.end.astimezone(UTC) - week.start.astimezone(UTC)
        self.assertEqual(elapsed, timedelta(hours=167))

    def test_containing_uses_local_time(self):
        self.assertEqual(Week.containing(paris(2026, 11, 1, 23, 30)).label, "2026-W44")
        self.assertEqual(Week.containing(paris(2026, 11, 2, 0, 10)).label, "2026-W45")
        self.assertEqual(Week.parse("2026-W01").shifted(-1).label, "2025-W52")

    def test_invalid_weeks_are_refused(self):
        for label in ("2026-44", "2025-W53", "2026-W00"):
            with self.subTest(label=label), self.assertRaises(ValueError):
                Week.parse(label)


class RankingTests(TestCase):
    def setUp(self):
        self.l1 = Level.objects.get(code="L1")
        self.mp = Level.objects.get(code="MP")
        self.week = Week.parse("2026-W44")
        self.sources = count(1)

    def member(self, name, **fields):
        return make_user(name, trust=TL.MEMBER, **fields)

    def credit(self, user, amount, *, at=None, level=None):
        return PointTransaction.objects.create(
            user=user,
            amount=amount,
            reason=Reason.SOLUTION_VALIDATED,
            source_type="test.source",
            source_id=next(self.sources),
            level=level,
            created_at=at or paris(2026, 10, 28, 12),
        )

    def board(self, **options):
        return [(e.username, e.points, e.rank) for e in standings(week=self.week, **options)]

    def test_points_count_for_the_week_and_the_level_of_the_exercise(self):
        lea, yanis = self.member("lea"), self.member("yanis")
        self.credit(lea, 20, level=self.l1)
        self.credit(lea, 15, level=self.mp)
        self.credit(yanis, 30, level=self.mp)
        self.credit(yanis, 50, at=paris(2026, 10, 25, 23, 59), level=self.mp)  # semaine précédente

        self.assertEqual(self.board(), [("lea", 35, 1), ("yanis", 30, 2)])
        self.assertEqual(self.board(level=self.mp), [("yanis", 30, 1), ("lea", 15, 2)])
        self.assertEqual(self.board(level=self.l1), [("lea", 20, 1)])
        # Panthéon : tous les points, depuis toujours.
        self.assertEqual([(e.username, e.points) for e in standings()], [("yanis", 80), ("lea", 35)])

    def test_ties_share_a_rank(self):
        for name, points in [("a", 10), ("b", 7), ("c", 7), ("d", 3)]:
            self.credit(self.member(name), points)
        self.assertEqual([rank for *_, rank in self.board()], [1, 2, 2, 4])

    def test_new_hidden_and_restricted_accounts_are_left_out(self):
        self.credit(self.member("lea"), 10)
        self.credit(make_user("nouveau", trust=TL.NEW), 10)
        self.credit(self.member("discret", leaderboard_visible=False), 10)
        self.credit(self.member("suspendu", status=User.Status.SUSPENDED), 10)
        self.credit(self.member("negatif"), -50)
        self.assertEqual(self.board(), [("lea", 10, 1)])

    def test_reversals_correct_a_week_only_during_consolidation(self):
        lea, yanis = self.member("lea"), self.member("yanis")
        early = self.credit(lea, 20, at=paris(2026, 11, 1, 20))
        late = self.credit(yanis, 20, at=paris(2026, 11, 1, 20))
        reverse(early, now=paris(2026, 11, 2, 10))  # dans les 24 h de consolidation
        reverse(late, now=paris(2026, 11, 3, 10))  # semaine déjà définitive

        self.assertEqual(self.board(), [("yanis", 20, 1)])
        self.week = self.week.shifted(1)
        self.assertEqual(self.board(), [])
        self.assertEqual(balance(yanis), 0)
        self.assertTrue(Week.parse("2026-W44").is_final(paris(2026, 11, 3)))
        self.assertFalse(Week.parse("2026-W44").is_final(paris(2026, 11, 2, 23)))

    def test_peers_and_neighbours(self):
        users = [self.member(f"m{i:02d}", level="PSI" if i % 2 else "MP") for i in range(20)]
        for points, user in enumerate(users, start=1):
            self.credit(user, points)

        entries = standings(week=self.week)
        index, around = neighbourhood(entries, users[9].pk)
        self.assertEqual(entries[index].rank, 11)
        self.assertEqual([e.points for e in around], [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5])
        peers = standings(week=self.week, peers_level=Level.objects.get(code="PSI"))
        self.assertEqual({e.declared_level for e in peers}, {"PSI"})
        self.assertEqual(len(peers), 10)


class LeaderboardApiTests(TestCase):
    def setUp(self):
        self.sources = count(1)

    def member(self, name, **fields):
        return make_user(name, trust=TL.MEMBER, **fields)

    def credit(self, user, amount):
        PointTransaction.objects.create(
            user=user,
            amount=amount,
            reason=Reason.SOLUTION_VALIDATED,
            source_type="test.source",
            source_id=next(self.sources),
        )

    def get(self, **params):
        return self.client.get("/api/leaderboards", params).json()

    def test_top_fifty_then_my_position_and_neighbours(self):
        users = [self.member(f"m{i:02d}") for i in range(60)]
        for points, user in enumerate(reversed(users), start=1):
            self.credit(user, points)
        self.client.force_login(users[57])

        board = self.get()

        self.assertEqual(board["total"], 60)
        self.assertEqual(len(board["top"]), 50)
        self.assertEqual(board["top"][0]["username"], "m00")
        self.assertEqual(board["me"]["rank"], 58)
        neighbours = board["me"]["neighbours"]
        self.assertEqual([e["rank"] for e in neighbours], [53, 54, 55, 56, 57, 58, 59, 60])
        self.assertTrue(neighbours[5]["is_me"])
        self.assertIsNone(board["next_week"])

    def test_a_new_account_is_told_why_it_is_not_ranked(self):
        self.client.force_login(make_user("nouveau", trust=TL.NEW))
        me = self.get(board="MP")["me"]
        self.assertIsNone(me["rank"])
        self.assertIn("niveau Membre", me["message"])

    def test_hiding_removes_me_from_rankings_and_my_public_points(self):
        lea = self.member("lea")
        self.credit(lea, 10)
        self.client.force_login(lea)

        response = self.client.post(
            "/api/auth/leaderboard-visibility", {"visible": False}, content_type="application/json"
        )

        self.assertFalse(response.json()["leaderboard_visible"])
        board = self.get()
        self.assertEqual(board["top"], [])
        self.assertIn("masqué", board["me"]["message"])
        self.assertIsNone(self.client.get("/api/members/lea").json()["points"])

    def test_unknown_boards_and_weeks_are_refused(self):
        self.assertEqual(self.client.get("/api/leaderboards", {"board": "X"}).status_code, 404)
        self.assertEqual(self.client.get("/api/leaderboards", {"week": "2026-W60"}).status_code, 422)

    def test_past_weeks_link_to_the_following_week(self):
        board = self.get(week="2026-W40")
        self.assertEqual((board["previous_week"], board["next_week"]), ("2026-W39", "2026-W41"))
        self.assertEqual((board["week_start"], board["week_end"]), ("2026-09-28", "2026-10-04"))


class PromotionTests(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(
            title="Exercice",
            statement="Énoncé.",
            difficulty_declared=1,
            primary_level=Level.objects.get(code="L1"),
        )

    def test_new_accounts_become_members_after_7_days_and_30_points(self):
        veteran = make_user("ancien", trust=TL.NEW, joined_days_ago=10)
        newcomer = make_user("recent", trust=TL.NEW, joined_days_ago=3)
        for user in (veteran, newcomer):
            award(user, Reason.SOLUTION_VALIDATED, self.exercise, amount=30)
            user.refresh_from_db()
        self.assertEqual((veteran.trust_level, newcomer.trust_level), (TL.MEMBER, TL.NEW))

        # L'ancienneté s'acquiert sans événement : le job nocturne fait la promotion.
        User.objects.filter(pk=newcomer.pk).update(date_joined=timezone.now() - timedelta(days=8))
        call_command("refresh_progress", stdout=StringIO())
        newcomer.refresh_from_db()
        self.assertEqual(newcomer.trust_level, TL.MEMBER)


class BadgeTests(ContentTestCase):
    def owned(self, user):
        return set(UserBadge.objects.filter(user=user).values_list("badge", flat=True))

    def validated(self, author, exercise=None, **fields):
        return Solution.objects.create(
            exercise=exercise or self.exercise,
            author=author,
            body="Preuve.",
            status=Solution.Status.VALIDATED,
            **fields,
        )

    def test_first_step_validated_and_pioneer_follow_the_review_flow(self):
        solution = self.publish()
        self.assertEqual(self.owned(self.student), {"premier-pas"})

        for reviewer in self.reviewers[:2]:
            self.review(solution, reviewer, Review.Verdict.CORRECT)

        self.assertEqual(self.owned(self.student), {"premier-pas", "valide", "pionnier"})
        second = self.publish(author=make_user("yanis", level="L1"))
        for reviewer in self.reviewers[:2]:
            self.review(second, reviewer, Review.Verdict.CORRECT)
        self.assertEqual(self.owned(second.author), {"premier-pas", "valide"})

    def test_a_generated_solution_earns_no_badge(self):
        self.validated(self.student, ai_usage=Solution.AiUsage.GENERATED)
        check_badges(self.student)
        self.assertNotIn("valide", self.owned(self.student))

    def test_author_needs_five_other_solvers(self):
        for i in range(4):
            self.validated(make_user(f"solveur{i}"))
        self.validated(self.author)
        check_badges(self.author)
        self.assertNotIn("auteur", self.owned(self.author))

        self.validated(make_user("solveur4"))
        check_badges(self.author)
        self.assertIn("auteur", self.owned(self.author))

    def test_reliable_reviewer_needs_25_reviews_and_85_percent_agreement(self):
        reviewer = self.reviewers[0]
        Review.objects.bulk_create(
            Review(
                solution=Solution.objects.create(exercise=self.exercise, author=self.student, body="."),
                reviewer=reviewer,
                agrees_with_consensus=i >= 4,
            )
            for i in range(25)
        )
        check_badges(reviewer)
        self.assertNotIn("relecteur-fiable", self.owned(reviewer))  # 21 sur 25 : 84 %

        disagreement = Review.objects.filter(reviewer=reviewer, agrees_with_consensus=False).first()
        disagreement.agrees_with_consensus = True
        disagreement.save()
        check_badges(reviewer)
        self.assertIn("relecteur-fiable", self.owned(reviewer))  # 22 sur 25 : 88 %

    def test_all_rounder_needs_five_topics(self):
        for topic in Topic.objects.all()[:5]:
            exercise = self.make_exercise()
            exercise.topics.add(topic)
            self.assertNotIn("touche-a-tout", self.owned(self.student))
            self.validated(self.student, exercise=exercise)
            check_badges(self.student)
        self.assertIn("touche-a-tout", self.owned(self.student))

    def test_elegance_needs_twenty_votes_that_count(self):
        solution = self.validated(self.student)
        voters = [make_user(f"votant{i}") for i in range(20)]
        # Le vote d'un compte de moins de 7 jours pèse 0 et ne compte pas.
        Vote.objects.bulk_create(
            Vote(voter=voter, solution=solution, weight=1 if i else 0) for i, voter in enumerate(voters)
        )
        check_badges(self.student)
        self.assertNotIn("elegance", self.owned(self.student))

        Vote.objects.filter(weight=0).update(weight=1)
        check_badges(self.student)
        self.assertIn("elegance", self.owned(self.student))

    def test_badges_are_awarded_once_and_listed_publicly(self):
        self.validated(self.student)
        self.assertEqual({b.slug for b in check_badges(self.student)}, {"premier-pas", "valide"})
        self.assertEqual(check_badges(self.student), [])

        catalog = self.client.get("/api/badges").json()
        self.assertEqual(len(catalog), 13)  # les 12 badges du document, plus Étudiant vérifié
        self.assertTrue(all(badge["available"] for badge in catalog))
        profile = self.client.get(f"/api/members/{self.student.username}").json()
        self.assertEqual({b["name"] for b in profile["badges"]}, {"Premier pas", "Validé !"})
