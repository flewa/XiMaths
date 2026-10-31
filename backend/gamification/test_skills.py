from django.test import SimpleTestCase

from catalog.models import Level, Topic
from content.models import Exercise, Solution
from content.tests import ContentTestCase, make_user

from . import skills
from .models import PointTransaction


class ContributorLevelTests(SimpleTestCase):
    def test_the_curve_is_quadratic_from_1_to_30(self):
        self.assertEqual(skills.contributor_level(0), {"level": 1, "points": 0, "floor": 0, "next": 20})
        self.assertEqual(skills.contributor_level(19)["level"], 1)
        self.assertEqual(skills.contributor_level(20)["level"], 2)
        self.assertEqual(skills.contributor_level(1619)["level"], 9)
        self.assertEqual(skills.contributor_level(1620), {"level": 10, "points": 1620, "floor": 1620, "next": 2000})
        self.assertEqual(skills.contributor_level(10**6), {"level": 30, "points": 10**6, "floor": 16820, "next": None})

    def test_a_negative_balance_stays_at_level_1(self):
        self.assertEqual(skills.contributor_level(-50)["level"], 1)
        self.assertEqual(skills.contributor_level(-50)["points"], 0)


class MasteryTests(SimpleTestCase):
    def test_mean_of_the_five_hardest_with_empty_slots_at_zero(self):
        self.assertEqual(skills.mastery([]), 0)
        self.assertEqual(skills.mastery([5]), 1)
        self.assertEqual(skills.mastery([3] * 5), 3)
        self.assertEqual(skills.mastery([1] * 20), 1)
        self.assertEqual(skills.mastery([5, 4, 4, 2, 1, 1, 1]), 3.2)


class SkillsMapTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.analysis = Topic.objects.get(slug="analyse")
        self.algebra = Topic.objects.get(slug="algebre-lineaire")

    def topic_exercise(self, difficulty, topic, *, level="L1", author=None, **fields):
        exercise = Exercise.objects.create(
            author=author or self.author,
            title=f"Exercice {Exercise.objects.count() + 1}",
            statement="Énoncé.",
            difficulty_declared=difficulty,
            primary_level=Level.objects.get(code=level),
            status=Exercise.Status.PUBLISHED,
            **fields,
        )
        exercise.topics.add(topic)
        return exercise

    def solve(self, exercise, *, ai_usage=Solution.AiUsage.NONE, status=Solution.Status.VALIDATED, author=None):
        return Solution.objects.create(
            exercise=exercise, author=author or self.student, body="Preuve.", ai_usage=ai_usage, status=status
        )

    def skill(self, topic):
        return next(entry for entry in skills.skills_map(self.student) if entry["topic"] == topic)

    def test_mastery_counts_validated_solutions_weighted_by_difficulty_and_ai_usage(self):
        self.solve(self.topic_exercise(4, self.analysis))
        self.solve(self.topic_exercise(4, self.analysis), ai_usage=Solution.AiUsage.IDEA)
        self.solve(self.topic_exercise(5, self.analysis), ai_usage=Solution.AiUsage.GENERATED)
        self.solve(self.topic_exercise(5, self.analysis), status=Solution.Status.UNDER_REVIEW)

        entry = self.skill(self.analysis)

        self.assertEqual(entry["mastery"], (4 + 2) / 5)
        self.assertEqual(entry["solved"], 2)
        self.assertEqual(self.skill(self.algebra)["mastery"], 0)

    def test_an_exercise_and_its_duplicates_count_once(self):
        canonical = self.topic_exercise(3, self.analysis)
        duplicate = self.topic_exercise(3, self.analysis, merged_into=canonical)
        duplicate.status = Exercise.Status.MERGED
        duplicate.save()
        self.solve(canonical)
        self.solve(duplicate)
        self.solve(canonical)

        self.assertEqual(self.skill(self.analysis)["solved"], 1)

    def test_the_estimated_difficulty_replaces_the_declared_one_after_five_ratings(self):
        self.solve(self.topic_exercise(1, self.analysis, difficulty_estimated=4.4, difficulty_ratings=5))
        self.solve(self.topic_exercise(1, self.analysis, difficulty_estimated=4.4, difficulty_ratings=4))

        self.assertEqual(self.skill(self.analysis)["mastery"], (4 + 1) / 5)

    def test_the_next_exercise_is_one_notch_above_mastery(self):
        for _ in range(5):
            self.solve(self.topic_exercise(2, self.analysis))
        too_easy = self.topic_exercise(2, self.analysis)
        just_above = self.topic_exercise(3, self.analysis)
        self.topic_exercise(5, self.analysis)
        self.solve(self.topic_exercise(3, self.analysis), status=Solution.Status.UNDER_REVIEW)  # déjà tenté
        self.topic_exercise(3, self.analysis, author=self.student)  # le sien
        self.topic_exercise(3, self.algebra)  # autre chapitre

        entry = self.skill(self.analysis)

        self.assertEqual((entry["mastery"], entry["target"]), (2, 3))
        self.assertEqual(entry["next"], just_above)
        self.assertNotEqual(entry["next"], too_easy)

    def test_exercises_beyond_the_declared_year_come_last(self):
        master = self.topic_exercise(1, self.analysis, level="M2")
        first_year = self.topic_exercise(4, self.analysis, level="L1")

        self.assertEqual(self.skill(self.analysis)["next"], first_year)
        self.student.declared_level = None
        self.assertEqual(self.skill(self.analysis)["next"], master)

    def test_mastery_tops_out_at_five(self):
        for _ in range(5):
            self.solve(self.topic_exercise(5, self.analysis))

        entry = self.skill(self.analysis)

        self.assertEqual((entry["mastery"], entry["target"], entry["next"]), (5, 5, None))


class ProgressApiTests(SkillsMapTests):
    def test_progress_carries_the_level_and_the_map(self):
        PointTransaction.objects.create(
            user=self.student, amount=90, reason=PointTransaction.Reason.SOLUTION_VALIDATED, source_type="t", source_id=1
        )
        self.solve(self.topic_exercise(3, self.analysis))
        suggestion = self.topic_exercise(1, self.analysis)
        self.client.force_login(self.student)

        data = self.client.get("/api/progress").json()

        self.assertEqual(data["contributor"], {"level": 3, "points": 90, "floor": 80, "next": 180})
        analysis = next(entry for entry in data["skills"] if entry["slug"] == "analyse")
        self.assertEqual(analysis["mastery"], 0.6)
        self.assertEqual(analysis["next"], {"id": suggestion.pk, "title": suggestion.title, "difficulty": 1})
        self.assertEqual(len(data["skills"]), Topic.objects.count())

    def test_the_public_level_hides_with_the_points(self):
        PointTransaction.objects.create(
            user=self.student, amount=90, reason=PointTransaction.Reason.SOLUTION_VALIDATED, source_type="t", source_id=1
        )
        self.assertEqual(self.client.get("/api/members/lea").json()["contributor_level"], 3)
        self.student.leaderboard_visible = False
        self.student.save()
        self.assertIsNone(self.client.get("/api/members/lea").json()["contributor_level"])

    def test_a_visitor_sees_no_one_elses_map(self):
        self.assertEqual(self.client.get("/api/progress").status_code, 401)
        self.client.force_login(make_user("autre"))
        self.assertEqual(self.client.get("/api/progress").json()["skills"][0]["solved"], 0)
