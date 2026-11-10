from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from catalog.models import Level
from training.challenges import group_of
from training.models import Challenge, ChallengeTemplate

from .editorial import EXERCISES
from .management.commands.import_exercises import EDITORIAL_USERNAME, problems
from .models import Exercise

User = get_user_model()


def run(*args):
    out = StringIO()
    call_command("import_exercises", *args, stdout=out)
    return out.getvalue()


class EditorialExercisesTests(TestCase):
    def test_every_exercise_passes_the_checks_of_the_site(self):
        self.assertEqual(problems(EXERCISES), [])

    def test_a_broken_exercise_is_reported(self):
        broken = {**EXERCISES[0], "final_answer": "import os", "statement": r"\def\x{1} $\x$"}
        found = problems([broken])
        self.assertTrue(any("LaTeX" in line for line in found))

    def test_dry_run_writes_nothing(self):
        self.assertIn(f"{len(EXERCISES)} exercices valides", run("--dry-run"))
        self.assertFalse(Exercise.objects.exists())
        self.assertFalse(User.objects.filter(username=EDITORIAL_USERNAME).exists())

    def test_import_publishes_everything_once(self):
        self.assertIn(f"Publiés : {len(EXERCISES)}.", run())
        self.assertEqual(Exercise.objects.filter(status=Exercise.Status.PUBLISHED).count(), len(EXERCISES))
        templates = sum("challenge" in spec for spec in EXERCISES)
        self.assertEqual(ChallengeTemplate.objects.count(), templates)
        # Un défi du jour, un seul, s'ouvre dans chaque groupe de niveaux qui a reçu un gabarit.
        levels = {spec["primary_level"] for spec in EXERCISES if "challenge" in spec}
        groups = {group_of(level)[0] for level in Level.objects.filter(code__in=levels)}
        self.assertEqual(Challenge.objects.count(), len(groups))

        self.assertIn(f"Déjà là : {len(EXERCISES)}.", run())
        self.assertEqual(Exercise.objects.count(), len(EXERCISES))

    def test_the_editorial_account_stays_out_of_the_way(self):
        run()
        account = User.objects.get(username=EDITORIAL_USERNAME)
        self.assertFalse(account.has_usable_password())
        self.assertFalse(account.leaderboard_visible)
        self.assertFalse(account.email_notifications)
        self.assertIsNotNone(account.email_verified_at)
