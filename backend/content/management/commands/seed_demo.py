"""Données de démonstration : quelques comptes, exercices et solutions relues.

Tout passe par les services métier, donc par les vraies règles de points.
Réservé au développement : tous les comptes partagent DEMO_PASSWORD et ont une
adresse email déjà vérifiée.
"""

import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import Level, Topic
from content.models import Exercise, Review, Solution
from content.services import cast_vote, publish_exercise, publish_solution, submit_review
from duplicates.services import index_exercise

User = get_user_model()
TL = User.TrustLevel

DEMO_PASSWORD = "demo-ximaths-2026"

USERS = [
    # (pseudo, niveau déclaré, niveau de confiance)
    ("camille", "M1", TL.EXPERT),
    ("relecteur1", "L3", TL.REVIEWER),
    ("relecteur2", "L3", TL.REVIEWER),
    ("relecteur3", "L3", TL.REVIEWER),
    ("lea", "L1", TL.MEMBER),
    ("yanis", "PSI", TL.MEMBER),
    # Accès à l'admin : file des doublons à arbitrer, modération.
    ("moderateur", "M2", TL.MODERATOR),
]

EXERCISES = [
    {
        "title": "Irrationalité de √2",
        "statement": "Montrer que $\\sqrt{2}$ n'est pas un nombre rationnel.",
        "hints": [
            "Raisonner par l'absurde avec une fraction irréductible $p/q$.",
            "Étudier la parité de $p$, puis celle de $q$.",
        ],
        "difficulty": 1,
        "level": "L1",
        "levels": ["L1"],
        "topics": ["arithmetique"],
        "solution": (
            "lea",
            "Supposons $\\sqrt{2} = p/q$ avec $p, q \\in \\N^*$ premiers entre eux. "
            "Alors $p^2 = 2q^2$, donc $p^2$ est pair, donc $p$ est pair : $p = 2k$.\n\n"
            "Il vient $4k^2 = 2q^2$, soit $q^2 = 2k^2$, donc $q$ est pair lui aussi. "
            "C'est absurde, puisque $p$ et $q$ sont premiers entre eux.",
            True,
        ),
    },
    {
        "title": "Une série de Riemann",
        "statement": "Montrer que la série $\\displaystyle\\sum_{n \\geq 1} \\frac{1}{n^2}$ converge.",
        "hints": ["Pour $n \\geq 2$, comparer $\\frac{1}{n^2}$ à $\\frac{1}{n(n-1)}$."],
        "difficulty": 2,
        "level": "L1",
        "levels": ["L1"],
        "topics": ["analyse"],
        "solution": (
            "yanis",
            "Pour $n \\geq 2$, $\\frac{1}{n^2} \\leq \\frac{1}{n(n-1)} = \\frac{1}{n-1} - \\frac{1}{n}$. "
            "Les sommes partielles de droite se télescopent et restent majorées par 1, "
            "donc la série à termes positifs $\\sum 1/n^2$ converge.",
            False,
        ),
    },
    {
        "title": "Rayon de convergence",
        "statement": (
            "Déterminer le rayon de convergence de la série entière\n\n"
            "$$\\sum_{n \\geq 0} \\frac{n^3}{2^n}\\, x^n.$$"
        ),
        "hints": ["Appliquer la règle de d'Alembert à $|u_n(x)|$."],
        "final_answer": "2",
        "difficulty": 3,
        "level": "L2",
        "levels": ["L2", "MP", "PSI"],
        "topics": ["analyse"],
        "solution": (
            "yanis",
            "Pour $x \\neq 0$, posons $u_n = \\frac{n^3}{2^n}|x|^n$. Alors\n\n"
            "$$\\frac{u_{n+1}}{u_n} = \\left(1 + \\frac{1}{n}\\right)^3 \\frac{|x|}{2} "
            "\\xrightarrow[n \\to \\infty]{} \\frac{|x|}{2}.$$\n\n"
            "D'après la règle de d'Alembert, la série converge si $|x| < 2$ et diverge "
            "si $|x| > 2$ : le rayon vaut $R = 2$.",
            True,
        ),
    },
    {
        "title": "Inverse de I − A pour A nilpotente",
        "statement": (
            "Soit $A \\in \\mathcal{M}_n(\\R)$ telle que $A^n = 0$. Montrer que $I_n - A$ "
            "est inversible et exprimer son inverse à l'aide des puissances de $A$."
        ),
        "hints": ["Développer $(I_n - A)(I_n + A + \\dots + A^{n-1})$."],
        "difficulty": 2,
        "level": "L2",
        "levels": ["L2", "MP"],
        "topics": ["algebre-lineaire"],
        "solution": None,
    },
]


class Command(BaseCommand):
    help = "Crée des comptes, exercices et solutions de démonstration."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo est réservé au développement (DEBUG=1).")
        if Exercise.objects.filter(author__username="camille").exists():
            self.stdout.write("Données de démonstration déjà présentes.")
            return

        rng = random.Random(42)
        joined = timezone.now() - timedelta(days=60)
        users = {}
        for username, level, trust in USERS:
            users[username] = User.objects.create_user(
                username,
                f"{username}@demo.ximaths.test",
                DEMO_PASSWORD,
                declared_level=Level.objects.get(code=level),
                trust_level=trust,
                date_joined=joined,
                email_verified_at=joined,
                is_staff=trust == TL.MODERATOR,
                is_superuser=trust == TL.MODERATOR,
            )

        for spec in EXERCISES:
            exercise = Exercise.objects.create(
                author=users["camille"],
                title=spec["title"],
                statement=spec["statement"],
                hints=spec["hints"],
                final_answer=spec.get("final_answer", ""),
                difficulty_declared=spec["difficulty"],
                primary_level=Level.objects.get(code=spec["level"]),
            )
            exercise.levels.set(Level.objects.filter(code__in=spec["levels"]))
            exercise.topics.set(Topic.objects.filter(slug__in=spec["topics"]))
            publish_exercise(exercise)
            index_exercise(exercise)

            if spec["solution"] is None:
                continue
            author, body, validate = spec["solution"]
            solution = publish_solution(
                Solution.objects.create(exercise=exercise, author=users[author], body=body),
                rng=rng,
            )
            if validate:
                for review in Review.objects.filter(solution=solution)[:2]:
                    submit_review(review, Review.Verdict.CORRECT)
            cast_vote(users["relecteur1"], exercise=exercise)

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(EXERCISES)} exercices de démonstration créés. "
                f"Comptes : {', '.join(users)} (mot de passe dans seed_demo.py)."
            )
        )
