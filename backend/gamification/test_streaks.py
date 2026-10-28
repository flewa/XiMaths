from datetime import date, datetime, time, timedelta

from django.utils import timezone

from config.errors import RuleError
from content.models import Review, Solution
from content.tests import ContentTestCase
from notifications.models import Notification
from training.models import TimedSession

from . import streaks
from .models import Goal, UserBadge, WeeklyStreak
from .rankings import Week

Status = WeeklyStreak.Status
# Novembre 2026 : cinq lundis, du 2 au 30.
W45, W46, W47, W48 = (Week.parse(f"2026-W{n}") for n in (45, 46, 47, 48))


def at(day, hour=12):
    return timezone.make_aware(datetime.combine(day, time(hour)))


class StreakTestCase(ContentTestCase):
    def attempt(self, user, day):
        solution = Solution.objects.create(exercise=self.exercise, author=user, body="Tentative.", status=Solution.Status.UNDER_REVIEW)
        Solution.objects.filter(pk=solution.pk).update(created_at=at(day))

    def active_week(self, user, week, days):
        for offset in range(days):
            self.attempt(user, week.monday + timedelta(days=offset))


class ActiveDayTests(StreakTestCase):
    def test_attempts_reviews_and_fifteen_minutes_of_clock_count(self):
        monday, tuesday, wednesday, thursday = (W46.monday + timedelta(days=n) for n in range(4))
        self.attempt(self.student, monday)
        solution = Solution.objects.create(exercise=self.exercise, author=self.author, body="Preuve.")
        Review.objects.create(solution=solution, reviewer=self.student, assigned_at=at(tuesday), submitted_at=at(tuesday))
        for day, seconds in ((wednesday, 15 * 60), (thursday, 5 * 60)):
            TimedSession.objects.create(
                user=self.student, exercise=self.exercise, duration_s=1800, started_at=at(day), elapsed_s=seconds,
                status=TimedSession.Status.SUBMITTED,
            )

        self.assertEqual(streaks.active_days(self.student, W46.start, W46.end), {monday, tuesday, wednesday})


class CloseWeekTests(StreakTestCase):
    def test_a_week_at_goal_is_achieved_and_summarised_neutrally(self):
        self.active_week(self.student, W45, 3)

        self.assertEqual(streaks.close_week(W45), 1)
        self.assertEqual(streaks.close_week(W45), 0)  # idempotent

        record = WeeklyStreak.objects.get(user=self.student)
        self.assertEqual((record.week, record.active_days, record.status), ("2026-W45", 3, Status.ACHIEVED))
        note = Notification.objects.get(user=self.student, kind=Notification.Kind.GOAL)
        self.assertNotIn("!", note.body)

    def test_two_jokers_a_month_protect_the_streak(self):
        self.active_week(self.student, W45, 3)
        for week in (W45, W46, W47, W48):
            streaks.close_week(week)

        statuses = list(WeeklyStreak.objects.filter(user=self.student).order_by("week").values_list("status", flat=True))
        self.assertEqual(statuses, [Status.ACHIEVED, Status.JOKER, Status.JOKER, Status.MISSED])
        self.assertEqual(streaks.streak_length(self.student), 0)

    def test_vacation_pauses_the_streak_without_breaking_it(self):
        self.active_week(self.student, W45, 3)
        streaks.close_week(W45)
        self.student.vacation_from, self.student.vacation_until = W46.monday, W47.sunday
        self.student.save()
        streaks.close_week(W46)
        streaks.close_week(W47)

        self.assertEqual(WeeklyStreak.objects.get(user=self.student, week=W46.label).status, Status.VACATION)
        self.assertEqual(streaks.streak_length(self.student), 1)

    def test_a_quiet_member_without_a_streak_gets_no_record(self):
        streaks.close_week(W45)
        self.assertFalse(WeeklyStreak.objects.exists())

    def test_four_achieved_weeks_earn_regular_bronze(self):
        for n in range(4):
            WeeklyStreak.objects.create(user=self.student, week=f"2026-W4{n}", goal=3, active_days=3, status=Status.ACHIEVED)
        self.active_week(self.student, W45, 3)
        streaks.close_week(W45)
        self.assertTrue(UserBadge.objects.filter(user=self.student, badge="regulier-bronze").exists())
        self.assertFalse(UserBadge.objects.filter(user=self.student, badge="regulier-argent").exists())


class SettingsTests(StreakTestCase):
    def test_goal_and_vacation_limits(self):
        with self.assertRaises(RuleError):
            streaks.set_goal(self.student, 1)
        today = date(2026, 11, 2)
        with self.assertRaises(RuleError):
            streaks.start_vacation(self.student, today + timedelta(weeks=5), today=today)
        streaks.start_vacation(self.student, today + timedelta(weeks=2), today=today)
        self.assertEqual(streaks.current_vacation(self.student, today), (today, today + timedelta(weeks=2)))
        streaks.end_vacation(self.student, today=today + timedelta(days=3))
        self.assertEqual(self.student.vacation_until, today + timedelta(days=2))

    def test_goal_progress_counts_distinct_exercises_since_creation(self):
        goal = streaks.create_goal(self.student, kind=Goal.Kind.SOLUTIONS, target=10, deadline=timezone.localdate() + timedelta(days=30))
        self.assertEqual(goal.title, "10 exercices")
        self.publish()
        self.publish(exercise=self.make_exercise())
        self.assertEqual(streaks.goal_progress(goal), (2, 10))


class ProgressApiTests(StreakTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.student)

    def test_progress_shows_the_week_and_accepts_settings(self):
        self.publish()
        data = self.client.get("/api/progress").json()
        self.assertEqual(data["goal_days"], 3)
        self.assertEqual(data["active_days"], 1)
        self.assertEqual(len(data["days"]), 7)
        self.assertEqual(data["jokers_left"], 2)

        self.assertEqual(self.client.put("/api/progress/goal", {"days": 5}, content_type="application/json").status_code, 204)
        until = (timezone.localdate() + timedelta(days=10)).isoformat()
        self.assertEqual(self.client.post("/api/progress/vacation", {"until": until}, content_type="application/json").status_code, 204)
        deadline = (timezone.localdate() + timedelta(days=60)).isoformat()
        created = self.client.post(
            "/api/goals", {"kind": "chrono_semaine", "target": 3, "deadline": deadline}, content_type="application/json"
        )
        self.assertEqual(created.status_code, 201)

        data = self.client.get("/api/progress").json()
        self.assertEqual(data["goal_days"], 5)
        self.assertIsNotNone(data["vacation"])
        self.assertEqual(data["goals"][0]["title"], "3 exercices chronométrés par semaine")
        self.assertEqual(self.client.delete(f"/api/goals/{created.json()['id']}").status_code, 204)
