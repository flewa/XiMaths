import math
import random
from collections import Counter
from datetime import timedelta

from django.utils import timezone

from .api import published_exercises
from .feed import EXPLORATION, TO_SOLVE, TRENDING, build_feed, compute_scores
from .models import Exercise, Solution, Vote
from .tests import ContentTestCase, make_user

Status = Solution.Status


class FeedTestCase(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.now = timezone.now()
        self.users = (make_user(f"solveur{i}") for i in range(1000))

    def published(self, *, days_ago=0, impressions=0, level="L1"):
        exercise = self.make_exercise(level=level)
        Exercise.objects.filter(pk=exercise.pk).update(
            published_at=self.now - timedelta(days=days_ago), feed_impressions=impressions
        )
        return exercise

    def solve(self, exercise, *, author=None, status=Status.VALIDATED, days_ago=0, **fields):
        return Solution.objects.create(
            exercise=exercise,
            author=author or next(self.users),
            body="Preuve.",
            status=status,
            published_at=self.now - timedelta(days=days_ago),
            **fields,
        )

    def scores(self, exercise):
        return compute_scores([Exercise.objects.get(pk=exercise.pk)], now=self.now)[exercise.pk]


class ScoreTests(FeedTestCase):
    def test_popularity_grows_logarithmically(self):
        for solutions, expected in [(1, 1.0), (10, 3.46), (100, 6.66)]:
            exercise = self.published()
            for _ in range(solutions):
                self.solve(exercise)
            self.assertAlmostEqual(self.scores(exercise).popular, expected, places=2)

    def test_one_solution_per_author_and_never_the_exercise_author(self):
        exercise = self.published()
        solver = make_user("yanis")
        self.solve(exercise, author=solver)
        self.solve(exercise, author=solver)
        self.solve(exercise, author=self.author)
        self.assertEqual(self.scores(exercise).popular, 1.0)

    def test_pending_solutions_count_0_4_and_generated_ones_nothing(self):
        exercise = self.published()
        self.solve(exercise, status=Status.UNDER_REVIEW)
        self.solve(exercise, ai_usage=Solution.AiUsage.GENERATED)
        self.solve(exercise, status=Status.NEEDS_WORK)
        self.assertAlmostEqual(self.scores(exercise).popular, math.log2(1.4))

    def test_trending_halves_a_solution_every_30_days(self):
        exercise = self.published(days_ago=60)
        self.solve(exercise, days_ago=30)
        scores = self.scores(exercise)
        self.assertAlmostEqual(scores.trending, math.log2(1.5))
        self.assertEqual(scores.popular, 1.0)

    def test_votes_and_the_canonical_bonus(self):
        exercise = self.published()
        self.solve(exercise)
        Vote.objects.create(voter=make_user("votant"), exercise=exercise, weight=1)
        self.assertAlmostEqual(self.scores(exercise).trending, 1.15)

        duplicate = self.published()
        Exercise.objects.filter(pk=duplicate.pk).update(
            status=Exercise.Status.MERGED, merged_into=exercise
        )
        self.assertAlmostEqual(self.scores(exercise).trending, 1.15 * 1.1)


class BuildFeedTests(FeedTestCase):
    def feed(self, **options):
        return build_feed(published_exercises(), now=self.now, rng=random.Random(0), **options)

    def test_the_feed_mixes_trending_to_solve_and_exploration(self):
        Exercise.objects.all().delete()
        for _ in range(15):
            # Anciens, avec une solution récente : tendances seulement.
            self.solve(self.published(days_ago=40), days_ago=1)
        fresh = {self.published(days_ago=3).pk for _ in range(8)}
        for _ in range(6):
            self.published(days_ago=20)  # récents, hors « À résoudre »

        feed = self.feed()

        self.assertEqual(len(feed), 20)
        self.assertEqual(len({exercise.pk for exercise, _ in feed}), 20)
        self.assertEqual(Counter(source for _, source in feed), {TRENDING: 12, TO_SOLVE: 5, EXPLORATION: 3})
        self.assertEqual(feed[0][1], TRENDING)
        self.assertTrue({e.pk for e, source in feed if source == TO_SOLVE} <= fresh)
        # Les sources sont réparties sur la page, pas regroupées.
        self.assertIn(TO_SOLVE, [source for _, source in feed[:4]])

    def test_a_small_pool_is_shown_entirely(self):
        Exercise.objects.all().delete()
        old = self.published(days_ago=90)
        self.published(days_ago=1)
        self.assertEqual(len(self.feed()), 2)
        self.assertIn(old.pk, [e.pk for e, _ in self.feed()])

    def test_least_seen_exercises_come_first(self):
        Exercise.objects.all().delete()
        seen = self.published(days_ago=1, impressions=500)
        unseen = self.published(days_ago=2, impressions=3)
        to_solve = [e.pk for e, source in self.feed(size=1)]
        self.assertEqual(to_solve, [unseen.pk])
        self.assertNotEqual(to_solve, [seen.pk])

    def test_an_exercise_with_two_validated_solutions_is_no_longer_to_solve(self):
        Exercise.objects.all().delete()
        exercise = self.published(days_ago=1)
        self.solve(exercise)
        self.solve(exercise)
        [(_, source)] = self.feed()
        self.assertEqual(source, TRENDING)


class FeedApiTests(FeedTestCase):
    def test_the_feed_says_why_each_exercise_is_there_and_counts_impressions(self):
        self.solve(self.published(days_ago=20))
        self.published(days_ago=2, level="MP")

        items = self.client.get("/api/feed", {"level": "L1"}).json()

        self.assertEqual(
            {(item["reason"], item["reason_label"]) for item in items},
            {("tendance", "Tendance"), ("a_resoudre", "À résoudre")},
        )
        self.assertNotIn("MP", {item["primary_level"] for item in items})
        self.assertEqual(
            set(Exercise.objects.filter(primary_level__code="L1").values_list("feed_impressions", flat=True)),
            {1},
        )
        self.assertEqual(self.client.get("/api/feed", {"level": "XX"}).status_code, 404)

    def test_the_list_sorts_by_popularity_or_keeps_the_unsolved(self):
        Exercise.objects.all().delete()
        quiet = self.published(days_ago=1)
        popular = self.published(days_ago=5)
        for _ in range(3):
            self.solve(popular)

        ids = lambda sort: [e["id"] for e in self.client.get("/api/exercises", {"sort": sort}).json()]
        self.assertEqual(ids("recent"), [quiet.pk, popular.pk])
        self.assertEqual(ids("popular"), [popular.pk, quiet.pk])
        self.assertEqual(ids("unsolved"), [quiet.pk])
