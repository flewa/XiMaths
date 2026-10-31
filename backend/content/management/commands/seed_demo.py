"""Données de démonstration : quelques comptes, une quinzaine d'exercices de la L1 au M1
et en prépa, des solutions relues ou en relecture, et les défis du jour ouverts.

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
from training.challenges import open_challenges
from training.models import ChallengeTemplate

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
        # Gabarit du défi du jour : chacun reçoit ses propres a et b.
        "challenge": {
            "statement": (
                "Déterminer le rayon de convergence de la série entière\n\n"
                "$$\\sum_{n \\geq 0} \\frac{n^{{a}}}{{{b}}^n}\\, x^n.$$"
            ),
            "parameters": {"a": [1, 2, 3, 4], "b": [2, 3, 5, 7]},
            "answer": "b",
        },
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
    {
        "title": "Série géométrique",
        "statement": "Soit $q \\in \\R$ avec $|q| < 1$. Calculer $\\displaystyle\\sum_{n \\geq 0} q^n$.",
        "hints": ["Écrire la somme partielle $S_N$ et calculer $(1 - q) S_N$."],
        "final_answer": "1/(1-q)",
        "challenge": {
            "statement": "Calculer $\\displaystyle\\sum_{n \\geq 0} \\frac{1}{{{a}}^n}$.",
            "parameters": {"a": [2, 3, 4, 5, 10]},
            "answer": "a/(a-1)",
        },
        "difficulty": 1,
        "level": "L1",
        "levels": ["L1", "MPSI", "PCSI"],
        "topics": ["analyse"],
        "solution": (
            "lea",
            "Pour $N \\in \\N$, posons $S_N = \\sum_{n=0}^{N} q^n$. Alors $(1 - q) S_N = 1 - q^{N+1}$, "
            "donc $S_N = \\frac{1 - q^{N+1}}{1 - q}$. Comme $|q| < 1$, $q^{N+1} \\to 0$ : la série converge "
            "et sa somme vaut $\\frac{1}{1 - q}$.",
            True,
        ),
    },
    {
        "title": "Inverse d'une matrice de rotation",
        "statement": (
            "Pour $\\theta \\in \\R$, on pose $R_\\theta = \\begin{pmatrix} \\cos\\theta & -\\sin\\theta \\\\ "
            "\\sin\\theta & \\cos\\theta \\end{pmatrix}$. Montrer que $R_\\theta$ est inversible et calculer son inverse."
        ),
        "hints": ["Calculer le déterminant.", "Que vaut $R_\\theta R_{-\\theta}$ ?"],
        "difficulty": 2,
        "level": "L1",
        "levels": ["L1", "MPSI"],
        "topics": ["algebre-lineaire"],
        "solution": None,
    },
    {
        "title": "Théorème de Wilson",
        "statement": "Soit $p$ un nombre premier. Montrer que $(p - 1)! \\equiv -1 \\pmod p$.",
        "hints": ["Dans $\\mathbb{Z}/p\\mathbb{Z}$, quels éléments sont leur propre inverse ?"],
        "difficulty": 3,
        "level": "L2",
        "levels": ["L2", "MP"],
        "topics": ["arithmetique"],
        "solution": None,
    },
    {
        "title": "Espérance et variance d'une loi de Poisson",
        "statement": "Soit $X$ une variable aléatoire de loi $\\mathcal{P}(\\lambda)$, avec $\\lambda > 0$. Calculer $E[X]$ et $V(X)$.",
        "hints": ["Calculer d'abord $E[X(X - 1)]$."],
        "final_answer": "lambda",
        "difficulty": 2,
        "level": "L2",
        "levels": ["L2", "MP", "PSI"],
        "topics": ["probabilites"],
        "author": "relecteur1",
        "solution": (
            "yanis",
            "On a $E[X] = \\sum_{k \\geq 1} k e^{-\\lambda} \\frac{\\lambda^k}{k!} = \\lambda e^{-\\lambda} "
            "\\sum_{k \\geq 1} \\frac{\\lambda^{k-1}}{(k-1)!} = \\lambda$. De même, $E[X(X-1)] = \\lambda^2$, "
            "donc $V(X) = E[X(X-1)] + E[X] - E[X]^2 = \\lambda^2 + \\lambda - \\lambda^2 = \\lambda$.",
            True,
        ),
    },
    {
        "title": "Seule valeur propre d'une matrice nilpotente",
        "statement": "Soit $N \\in \\mathcal{M}_n(\\mathbb{C})$ nilpotente. Montrer que $0$ est sa seule valeur propre.",
        "hints": ["Si $N x = \\mu x$ avec $x \\neq 0$, que vaut $N^k x$ ?"],
        "difficulty": 2,
        "level": "MP",
        "levels": ["MP", "PSI", "L2"],
        "topics": ["algebre-lineaire"],
        "solution": (
            "yanis",
            "Soit $k$ tel que $N^k = 0$. Si $N x = \\mu x$ avec $x \\neq 0$, alors $N^k x = \\mu^k x = 0$, "
            "donc $\\mu^k = 0$ et $\\mu = 0$. Enfin $N$ n'est pas inversible (sinon $N^k$ le serait), "
            "donc $0$ est bien valeur propre : c'est la seule.",
            False,
        ),
    },
    {
        "title": "Ensemble des barycentres à poids positifs",
        "statement": (
            "Soit $A_1, \\dots, A_n$ des points du plan. Montrer que l'ensemble des barycentres des $A_i$ "
            "affectés de poids positifs (de somme non nulle) est convexe."
        ),
        "hints": ["Associativité du barycentre."],
        "difficulty": 2,
        "level": "PSI",
        "levels": ["PSI", "PT", "PC"],
        "topics": ["geometrie"],
        "solution": None,
    },
    {
        "title": "Lemme de Borel–Cantelli",
        "statement": (
            "Soit $(A_n)_{n \\geq 0}$ une suite d'événements telle que $\\sum_n P(A_n) < +\\infty$. "
            "Montrer que $P\\left(\\limsup_{n} A_n\\right) = 0$."
        ),
        "hints": ["$\\limsup A_n = \\bigcap_{N} \\bigcup_{n \\geq N} A_n$."],
        "difficulty": 3,
        "level": "L3",
        "levels": ["L3", "M1"],
        "topics": ["probabilites"],
        "solution": (
            "relecteur2",
            "Pour tout $N$, $\\limsup A_n \\subset \\bigcup_{n \\geq N} A_n$, donc "
            "$P(\\limsup A_n) \\leq \\sum_{n \\geq N} P(A_n)$, reste d'une série convergente : il tend vers 0 "
            "quand $N \\to +\\infty$. D'où $P(\\limsup A_n) = 0$.",
            True,
        ),
    },
    {
        "title": "Théorème de Heine",
        "statement": (
            "Soit $(E, d)$ un espace métrique et $K \\subset E$ compact. Montrer que toute fonction continue "
            "$f : K \\to \\R$ est uniformément continue."
        ),
        "hints": ["Raisonner par l'absurde et extraire des sous-suites convergentes."],
        "difficulty": 3,
        "level": "L3",
        "levels": ["L3"],
        "topics": ["topologie"],
        "solution": None,
    },
    {
        "title": "Groupe d'ordre premier",
        "statement": "Montrer qu'un groupe fini d'ordre premier est cyclique.",
        "hints": ["Théorème de Lagrange."],
        "difficulty": 2,
        "level": "L3",
        "levels": ["L3", "MP"],
        "topics": ["algebre"],
        "author": "relecteur1",
        "solution": None,
    },
    {
        "title": "Intégrale de Gauss",
        "statement": "Calculer $\\displaystyle\\int_{-\\infty}^{+\\infty} e^{-x^2}\\, dx$.",
        "hints": ["Passer en coordonnées polaires dans le carré de l'intégrale."],
        "final_answer": "sqrt(pi)",
        "difficulty": 4,
        "level": "M1",
        "levels": ["M1", "L3"],
        "topics": ["analyse"],
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
            self.challenge_templates()
            open_challenges()
            self.stdout.write("Données de démonstration déjà présentes ; défis du jour ouverts.")
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
                author=users[spec.get("author", "camille")],
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
            voter = "relecteur2" if spec.get("author") == "relecteur1" else "relecteur1"
            cast_vote(users[voter], exercise=exercise)

        self.challenge_templates()
        open_challenges()
        self.stdout.write(
            self.style.SUCCESS(
                f"{len(EXERCISES)} exercices de démonstration créés. "
                f"Comptes : {', '.join(users)} (mot de passe dans seed_demo.py)."
            )
        )

    def challenge_templates(self):
        """Gabarits du défi du jour, ajoutés aussi à une base déjà remplie."""
        for spec in EXERCISES:
            exercise = Exercise.objects.filter(title=spec["title"]).first()
            if "challenge" in spec and exercise is not None:
                ChallengeTemplate.objects.get_or_create(exercise=exercise, defaults=spec["challenge"])
