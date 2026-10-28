from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import TestCase

from content.management.commands.run_jobs import next_hour, run, weekly_digests

PARIS = ZoneInfo("Europe/Paris")


class JobsTests(TestCase):
    def test_a_failing_job_does_not_stop_the_others(self):
        done = []

        def broken(now):
            raise RuntimeError("panne")

        with self.assertLogs("ximaths.jobs", level="INFO") as logs:
            failures = run({"cassée": broken, "suivante": lambda now: done.append(now)}, "maintenant")

        self.assertEqual(failures, 1)
        self.assertEqual(done, ["maintenant"])
        self.assertTrue(any("cassée" in line for line in logs.output))

    def test_digests_wait_for_monday_morning(self):
        sunday_noon = datetime(2026, 10, 25, 12, tzinfo=PARIS)
        monday_night = datetime(2026, 10, 26, 3, tzinfo=PARIS)
        self.assertEqual(weekly_digests(sunday_noon), 0)
        self.assertEqual(weekly_digests(monday_night), 0)

    def test_the_loop_wakes_up_on_the_hour(self):
        self.assertEqual(next_hour(datetime(2026, 10, 28, 18, 42, 7, tzinfo=PARIS)), datetime(2026, 10, 28, 19, tzinfo=PARIS))
