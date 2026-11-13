"""Titres d'exercices en LaTeX : formules entre $…$, version texte pour les moteurs et les
notifications, validation des titres proposés."""

from django.test import SimpleTestCase

from notifications.models import Notification
from notifications.services import notify

from .editorial import EXERCISES
from .latex import plain_math, title_problems
from .tests import ContentTestCase, make_user


class PlainMathTests(SimpleTestCase):
    def test_formulas_are_written_out_in_unicode(self):
        cases = {
            r"Reste de $3^{100}$ modulo 7": "Reste de 3¹⁰⁰ modulo 7",
            r"Suite récurrente $u_{n+1} = \sqrt{2 + u_n}$ : convergence": "Suite récurrente uₙ₊₁ = √(2 + uₙ) : convergence",
            r"Intégrale de $e^{-2x} \sin(3x)$ sur $[0, +\infty[$": "Intégrale de e⁻²ˣ sin(3x) sur [0, +∞[",
            r"$\Q$ n'est pas un $G_\delta$ de $\R$": "ℚ n'est pas un G_δ de ℝ",
            r"Partie entière : $\lfloor 2x \rfloor = \lfloor x \rfloor$": "Partie entière : ⌊2x⌋ = ⌊x⌋",
            r"Somme des $k \binom{n}{k}$": "Somme des k (k parmi n)",
            r"Éléments d'ordre 2 de $\mathfrak{S}_4$": "Éléments d'ordre 2 de 𝔖₄",
            r"Équation $\operatorname{ch} x = 2$": "Équation ch x = 2",
            r"Intégrale de $e^{-x^2 - y^2}$": "Intégrale de e^(−x² − y²)",
            "Longueur de l'astroïde": "Longueur de l'astroïde",
        }
        for latex, text in cases.items():
            with self.subTest(latex=latex):
                self.assertEqual(plain_math(latex), text)

    def test_every_editorial_title_reads_as_plain_text(self):
        for exercise in EXERCISES:
            with self.subTest(title=exercise["title"]):
                text = plain_math(exercise["title"])
                self.assertEqual(title_problems(exercise["title"]), [])
                self.assertNotIn("$", text)
                self.assertNotIn("\\", text)

    def test_a_title_needs_closed_formulas_and_allowed_commands(self):
        self.assertEqual(len(title_problems("Reste de $3^{100} modulo 7")), 1)
        self.assertIn("\\input", title_problems(r"Titre $\input{x}$")[0])


class TitleApiTests(ContentTestCase):
    def test_the_api_gives_the_title_and_its_text(self):
        self.exercise.title = r"Reste de $3^{100}$ modulo 7"
        self.exercise.save()
        [item] = self.client.get("/api/exercises").json()
        self.assertEqual((item["title"], item["title_text"]), (r"Reste de $3^{100}$ modulo 7", "Reste de 3¹⁰⁰ modulo 7"))

    def test_notifications_write_formulas_out(self):
        user = make_user("membre")
        notify(user, Notification.Kind.BADGE, r"Ton exercice « $x^n$ »", r"Sur $\R$.")
        notification = user.notifications.get()
        self.assertEqual((notification.title, notification.body), ("Ton exercice « xⁿ »", "Sur ℝ."))
