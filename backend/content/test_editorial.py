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


class FilieresTests(TestCase):
    """Prépas BCPST, ECG, B/L et MPI : des exercices déjà publiés les rejoignent."""

    def test_every_new_level_has_exercises(self):
        for code in ["MPI", "BCPST1", "BCPST2", "ECG1", "ECG2", "BL1", "BL2"]:
            count = sum(code in spec["levels"] for spec in EXERCISES)
            self.assertGreaterEqual(count, 10, code)

    def test_mp_exercises_are_also_mpi(self):
        self.assertTrue(all("MPI" in spec["levels"] for spec in EXERCISES if "MP" in spec["levels"]))

    def test_no_complex_numbers_nor_differential_equations_in_ecg_and_bl(self):
        outside = {"nombres-complexes", "equations-differentielles", "determinants"}
        for spec in EXERCISES:
            if {"ECG1", "ECG2", "BL1", "BL2"} & set(spec["levels"]):
                self.assertFalse(outside & set(spec["topics"]), spec["title"])

    def test_an_exercise_already_published_gains_its_new_levels(self):
        run()
        spec = next(spec for spec in EXERCISES if "BCPST1" in spec["levels"] and spec["primary_level"] != "BCPST1")
        exercise = Exercise.objects.get(title=spec["title"])
        exercise.levels.remove(Level.objects.get(code="BCPST1"))
        l3 = Level.objects.get(code="M2")
        exercise.levels.add(l3)

        self.assertIn("Mis à jour : 1.", run())
        codes = set(exercise.levels.values_list("code", flat=True))
        # Le niveau manquant revient ; celui qu'on avait ajouté à la main n'est pas retiré.
        self.assertIn("BCPST1", codes)
        self.assertIn("M2", codes)

    def test_a_correction_of_the_editorial_reaches_the_published_exercise(self):
        run()
        spec = next(spec for spec in EXERCISES if spec["title"].startswith("Ruine du joueur"))
        exercise = Exercise.objects.get(title=spec["title"])
        # L'exercice tel qu'il était publié avant la correction.
        Exercise.objects.filter(pk=exercise.pk).update(statement="Ancien énoncé.", hints=["Ancienne indication."], final_answer="3/10")

        self.assertIn("Mis à jour : 1.", run())
        exercise.refresh_from_db()
        self.assertEqual(exercise.statement, spec["statement"].strip())
        self.assertEqual(exercise.final_answer, "7/10")
        self.assertEqual(len(exercise.hints), len(spec["hints"]))

    def test_an_exercise_corrected_by_the_team_keeps_its_content(self):
        from django.utils import timezone

        run()
        spec = next(spec for spec in EXERCISES if spec["title"].startswith("Ruine du joueur"))
        Exercise.objects.filter(title=spec["title"]).update(statement="Version de l'équipe.", edited_by_team_at=timezone.now())
        run()
        self.assertEqual(Exercise.objects.get(title=spec["title"]).statement, "Version de l'équipe.")

    def test_the_classics_of_lot_5_are_statements_for_mp_without_answers(self):
        from .editorial.lot5 import EXERCISES as LOT5

        self.assertEqual(len(LOT5), 31)
        for spec in LOT5:
            self.assertIn("MP", spec["levels"], spec["title"])
            self.assertFalse(spec.get("final_answer"), spec["title"])
