"""Niveau de contributeur et carte de compétences.

Niveau de contributeur, de 1 à 30, sur une courbe quadratique : le niveau n demande
20 (n − 1)² points, soit 20 points pour le niveau 2, 1 620 pour le 10 et 16 820 pour le 30.
Il suit le solde du ledger, et redescend donc si des points frauduleux sont annulés.

Carte de compétences : dans chaque chapitre, la maîtrise (de 0 à 5) est la moyenne des
difficultés de tes 5 exercices résolus les plus difficiles, une case vide comptant 0.
Cinq exercices de difficulté 3 donnent 3 ; un seul exercice de difficulté 5 donne 1. Une
solution avec l'aide de l'IA sur une idée compte pour moitié, une solution générée pas du
tout, comme au barème. Le prochain exercice proposé vise un cran au-dessus.
"""

import math
from collections import defaultdict

from django.db.models import Case, F, FloatField, IntegerField, Value, When
from django.db.models.functions import Abs, Cast

from catalog.models import Topic
from content.models import MIN_DIFFICULTY_RATINGS, Exercise, Solution

from .scoring import AI_USAGE_FACTOR

MAX_LEVEL = 30
LEVEL_STEP = 20
MASTERY_SAMPLE = 5
MAX_DIFFICULTY = 5


def level_threshold(level):
    """Points qu'il faut pour atteindre `level`."""
    return LEVEL_STEP * (level - 1) ** 2


def contributor_level(points):
    """Niveau atteint avec `points`, et les seuils qui l'encadrent (None au niveau 30)."""
    points = max(0, points)
    level = min(MAX_LEVEL, 1 + math.isqrt(points // LEVEL_STEP))
    return {
        "level": level,
        "points": points,
        "floor": level_threshold(level),
        "next": level_threshold(level + 1) if level < MAX_LEVEL else None,
    }


def mastery(difficulties):
    """Moyenne des 5 meilleures valeurs, les cases vides comptant 0."""
    best = sorted(difficulties, reverse=True)[:MASTERY_SAMPLE]
    return sum(best) / MASTERY_SAMPLE


def solved_by_topic(user):
    """{topic_id: {exercice: difficulté pondérée}} pour les solutions validées de `user`.

    Un exercice ne compte qu'une fois par chapitre, au niveau de son canonique s'il a été
    fusionné : plusieurs solutions d'un même exercice, ou d'un doublon, n'en font qu'une.
    """
    solutions = (
        Solution.objects.filter(author=user, status=Solution.Status.VALIDATED)
        .exclude(ai_usage=Solution.AiUsage.GENERATED)
        .exclude(exercise__status=Exercise.Status.REMOVED)
        .select_related("exercise")
        .prefetch_related("exercise__topics")
    )
    solved = defaultdict(dict)
    for solution in solutions:
        exercise = solution.exercise
        key = exercise.merged_into_id or exercise.pk
        value = exercise.difficulty * AI_USAGE_FACTOR[solution.ai_usage]
        for topic in exercise.topics.all():
            solved[topic.pk][key] = max(value, solved[topic.pk].get(key, 0))
    return solved


def _effective_difficulty():
    """Difficulté retenue par le barème (Exercise.difficulty), calculée en base."""
    return Case(
        When(
            difficulty_estimated__isnull=False,
            difficulty_ratings__gte=MIN_DIFFICULTY_RATINGS,
            then=F("difficulty_estimated"),
        ),
        default=Cast("difficulty_declared", FloatField()),
        output_field=FloatField(),
    )


def suggest(user, topic, target):
    """Exercice publié du chapitre, au plus près de la difficulté `target`, que `user`
    n'a ni écrit ni tenté. Ceux de son année d'études ou d'avant passent en premier."""
    year = user.declared_level.year if user.declared_level else None
    candidates = (
        Exercise.objects.filter(status=Exercise.Status.PUBLISHED, topics=topic)
        .exclude(author=user)
        .exclude(solutions__author=user)
        .annotate(
            effective=_effective_difficulty(),
            beyond=Case(
                When(primary_level__year__gt=year, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
            if year
            else Value(0, output_field=IntegerField()),
        )
        .annotate(distance=Abs(F("effective") - target))
        .order_by("beyond", "distance", "-published_at", "pk")
    )
    return candidates.first()


def skills_map(user):
    """Maîtrise de `user` dans chaque chapitre, avec le prochain exercice proposé."""
    solved = solved_by_topic(user)
    topics = []
    for topic in Topic.objects.all():
        values = solved.get(topic.pk, {}).values()
        level = mastery(values)
        target = min(MAX_DIFFICULTY, math.floor(level) + 1)
        topics.append(
            {
                "topic": topic,
                "mastery": level,
                "solved": len(values),
                "target": target,
                "next": suggest(user, topic, target),
            }
        )
    return topics
