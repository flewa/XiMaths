"""Mise en avant des exercices : scores Tendances et Populaires, fil d'accueil.

La mise en avant croît avec le nombre de solutions, mais de façon logarithmique :
cent fois plus de solutions ne donnent qu'un score sept fois plus élevé.

    T(e) = log2(1 + Σ w(s)·2^(−t_s/30)) × (1 + 0,15·log2(1 + V30)) × Q(e)
    P(e) = log2(1 + Σ w(s))             × (1 + 0,15·log2(1 + V))   × Q(e)

- La somme porte sur une solution par auteur, la mieux notée, hors auteur de
  l'exercice et comptes liés à lui.
- w(s) : 1 validée, 0,4 en relecture, 0 sinon ou si elle est générée par IA.
- t_s : âge de la solution en jours.
- V, V30 : votes « utile » sur l'exercice, pondérés, au total et sur 30 jours.
- Q(e) : 0,5 si un signalement de l'exercice est en cours, 1,1 pour l'exercice
  canonique d'un cluster de doublons fusionnés, 1 sinon.

Le fil mélange 60 % de Tendances, 25 % d'« À résoudre » et 15 % d'exploration.
Il tient sur une page : pas de défilement infini.
"""

import math
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta

from django.db.models import F, Q, Sum
from django.utils import timezone

from accounts.models import AccountLink
from moderation.models import Report

from .models import Exercise, Solution, Vote

SOLUTION_WEIGHTS = {
    Solution.Status.VALIDATED: 1.0,
    Solution.Status.UNDER_REVIEW: 0.4,
    Solution.Status.CONTESTED: 0.4,
}
HALF_LIFE_DAYS = 30
VOTE_FACTOR = 0.15
RECENT_VOTES_DAYS = 30
CANONICAL_BONUS = 1.1
REPORTED_PENALTY = 0.5

FEED_SIZE = 20
TRENDING, TO_SOLVE, EXPLORATION = "tendance", "a_resoudre", "exploration"
FEED_MIX = {TRENDING: 0.60, TO_SOLVE: 0.25, EXPLORATION: 0.15}
FEED_LABELS = {TRENDING: "Tendance", TO_SOLVE: "À résoudre", EXPLORATION: "À découvrir"}
# « À résoudre » : moins de 14 jours et moins de 2 solutions validées.
TO_SOLVE_MAX_AGE = timedelta(days=14)
TO_SOLVE_MAX_SOLUTIONS = 2
# Exploration : exercices de moins de 30 jours, tirés au hasard, en priorité ceux
# qui n'ont pas encore eu leur exposition minimale.
EXPLORATION_MAX_AGE = timedelta(days=30)
MIN_IMPRESSIONS = 200


@dataclass(frozen=True)
class Scores:
    trending: float
    popular: float


def _days(delta):
    return max(delta.total_seconds(), 0) / 86400


def compute_scores(exercises, *, now=None):
    """{pk: Scores} pour ces exercices."""
    now = now or timezone.now()
    authors = {exercise.pk: exercise.author_id for exercise in exercises}
    linked = defaultdict(set)
    author_ids = {author for author in authors.values() if author}
    for first, second in AccountLink.objects.filter(
        Q(user_a_id__in=author_ids) | Q(user_b_id__in=author_ids)
    ).values_list("user_a_id", "user_b_id"):
        linked[first].add(second)
        linked[second].add(first)
    # Meilleure contribution de chaque auteur de solution, par exercice.
    decayed = defaultdict(dict)
    plain = defaultdict(dict)
    solutions = (
        Solution.objects.filter(exercise_id__in=authors, status__in=SOLUTION_WEIGHTS)
        .exclude(ai_usage=Solution.AiUsage.GENERATED)
        .values_list("exercise_id", "author_id", "status", "published_at")
    )
    for exercise_id, author_id, status, published_at in solutions:
        exercise_author = authors[exercise_id]
        if author_id is None or author_id == exercise_author or author_id in linked[exercise_author]:
            continue
        weight = SOLUTION_WEIGHTS[status]
        age = _days(now - published_at) if published_at else 0
        decay = 2 ** (-age / HALF_LIFE_DAYS)
        plain[exercise_id][author_id] = max(plain[exercise_id].get(author_id, 0), weight)
        decayed[exercise_id][author_id] = max(decayed[exercise_id].get(author_id, 0), weight * decay)

    votes = {
        row["exercise_id"]: row
        for row in Vote.objects.filter(exercise_id__in=authors)
        .values("exercise_id")
        .annotate(
            total=Sum("weight"),
            recent=Sum("weight", filter=Q(created_at__gte=now - timedelta(days=RECENT_VOTES_DAYS))),
        )
    }
    canonical = set(
        Exercise.objects.filter(merged_into_id__in=authors).values_list("merged_into_id", flat=True)
    )
    reported = set(
        Report.objects.filter(exercise_id__in=authors, status=Report.Status.OPEN).values_list(
            "exercise_id", flat=True
        )
    )

    scores = {}
    for pk in authors:
        row = votes.get(pk, {})
        quality = REPORTED_PENALTY if pk in reported else (CANONICAL_BONUS if pk in canonical else 1.0)
        recent_votes = float(row.get("recent") or 0)
        all_votes = float(row.get("total") or 0)
        scores[pk] = Scores(
            trending=math.log2(1 + sum(decayed[pk].values()))
            * (1 + VOTE_FACTOR * math.log2(1 + recent_votes))
            * quality,
            popular=math.log2(1 + sum(plain[pk].values()))
            * (1 + VOTE_FACTOR * math.log2(1 + all_votes))
            * quality,
        )
    return scores


def _quotas(size):
    """Répartit `size` places selon FEED_MIX, au plus fort reste : 20 → 12, 5, 3."""
    exact = {source: share * size for source, share in FEED_MIX.items()}
    quotas = {source: math.floor(value) for source, value in exact.items()}
    by_remainder = sorted(exact, key=lambda source: exact[source] - quotas[source], reverse=True)
    for source in by_remainder[: size - sum(quotas.values())]:
        quotas[source] += 1
    return quotas


def build_feed(exercises, *, now=None, rng=None, size=FEED_SIZE):
    """Fil d'accueil : [(exercice, source)], sources entrelacées au fil de la page.

    `exercises` : les exercices publiés du niveau, annotés de `validated_solutions`.
    Une source épuisée cède sa place aux autres, puis aux plus récents."""
    now = now or timezone.now()
    rng = rng or random.Random()
    pool = list(exercises)
    scores = compute_scores(pool, now=now)
    newest_first = sorted(pool, key=lambda e: e.published_at, reverse=True)

    trending = sorted(
        (e for e in pool if scores[e.pk].trending > 0),
        key=lambda e: (-scores[e.pk].trending, -e.published_at.timestamp()),
    )
    # Les moins vus d'abord : c'est ce qui garantit l'exposition des nouveaux.
    to_solve = sorted(
        (
            e
            for e in pool
            if now - e.published_at < TO_SOLVE_MAX_AGE
            and e.validated_solutions < TO_SOLVE_MAX_SOLUTIONS
        ),
        key=lambda e: (e.feed_impressions, -e.published_at.timestamp()),
    )
    recent = [e for e in newest_first if now - e.published_at < EXPLORATION_MAX_AGE]
    underexposed = [e for e in recent if e.feed_impressions < MIN_IMPRESSIONS]
    exposed = [e for e in recent if e.feed_impressions >= MIN_IMPRESSIONS]
    exploration = rng.sample(underexposed, len(underexposed)) + rng.sample(exposed, len(exposed))
    sources = {TRENDING: trending, TO_SOLVE: to_solve, EXPLORATION: exploration}

    count = min(size, len(pool))
    quotas = _quotas(count)
    taken = dict.fromkeys(quotas, 0)
    seen = set()
    feed = []
    for slot in range(count):
        # D'abord la source la plus en retard sur sa part, à ce point de la page.
        for source in sorted(quotas, key=lambda s: taken[s] - quotas[s] * (slot + 1) / count):
            exercise = next((e for e in sources[source] if e.pk not in seen), None)
            if exercise is not None:
                break
        else:
            # Toutes les sources sont épuisées : les plus récents restants.
            exercise = next(e for e in newest_first if e.pk not in seen)
            source = EXPLORATION
        seen.add(exercise.pk)
        taken[source] += 1
        feed.append((exercise, source))
    return feed


def record_impressions(feed):
    """Compte un affichage pour chaque exercice du fil."""
    Exercise.objects.filter(pk__in=[exercise.pk for exercise, _ in feed]).update(
        feed_impressions=F("feed_impressions") + 1
    )
