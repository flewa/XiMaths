"""Barème XiMaths : toutes les valeurs du document de conception, à un seul endroit."""

import math

from .models import PointTransaction

Reason = PointTransaction.Reason

POINTS = {
    Reason.EXERCISE_PUBLISHED: 5,
    Reason.EXERCISE_SOLVED: 3,
    Reason.EXERCISE_UPVOTED: 1,
    Reason.SOLUTION_ATTEMPT: 2,
    Reason.SOLUTION_VALIDATED: 15,
    Reason.FIRST_VALIDATED: 10,
    Reason.SOLUTION_UPVOTED: 2,
    Reason.SOLUTION_RECOMMENDED: 5,
    Reason.REVIEW_AGREED: 2,
    Reason.REPORT_CONFIRMED: 3,
    Reason.PLAGIARISM_PENALTY: -50,
}

# Multiplicateur d'une solution validée selon la difficulté de l'exercice (1 à 5).
DIFFICULTY_MULTIPLIER = {1: 1.0, 2: 1.25, 3: 1.5, 4: 2.0, 5: 2.5}

# Facteur selon l'usage de l'IA déclaré (valeurs de Solution.AiUsage).
AI_USAGE_FACTOR = {
    "aucune": 1.0,
    "relecture": 1.0,
    "aide_idee": 0.5,
    "generee": 0.0,
}

# Nombre d'occurrences rémunérées par jour.
DAILY_COUNT_CAPS = {
    Reason.EXERCISE_PUBLISHED: 3,
    Reason.SOLUTION_ATTEMPT: 5,
    Reason.REVIEW_AGREED: 15,
}

# Les actions que personne d'autre n'a encore validées partagent un plafond quotidien.
UNVALIDATED_REASONS = frozenset(DAILY_COUNT_CAPS)
UNVALIDATED_DAILY_CAP = 40

# Passage automatique de Nouveau à Membre, qui ouvre les classements.
MEMBER_MIN_DAYS = 7
MEMBER_MIN_POINTS = 30

# Plafonds par cible : par exercice pour EXERCISE_*, par solution pour SOLUTION_UPVOTED.
PER_TARGET_CAPS = {
    Reason.EXERCISE_SOLVED: 30,
    Reason.EXERCISE_UPVOTED: 20,
    Reason.SOLUTION_UPVOTED: 20,
}


def validated_solution_points(difficulty, ai_usage):
    """Points d'une solution validée : 15 × m(d) × facteur IA, arrondi au demi supérieur."""
    base = POINTS[Reason.SOLUTION_VALIDATED]
    return math.floor(base * DIFFICULTY_MULTIPLIER[difficulty] * AI_USAGE_FACTOR[ai_usage] + 0.5)
