"""Badges du MVP : publics, critères affichés, aucun badge secret.

check_badges est appelé après chaque événement qui peut en débloquer un, et
chaque nuit par refresh_progress en filet de sécurité. Un badge obtenu reste acquis.
"""

from collections.abc import Callable
from dataclasses import dataclass

from django.db.models import Count, Q
from django.utils import timezone

from content.models import Exercise, Review, Solution
from moderation.models import Report

from .models import PointTransaction, UserBadge

AUTHOR_SOLVERS = 5
RELIABLE_REVIEWS = 25
RELIABLE_AGREEMENT = 0.85
ALL_ROUNDER_TOPICS = 5
ELEGANCE_VOTES = 20


@dataclass(frozen=True)
class Badge:
    slug: str
    name: str
    criterion: str
    # None : le badge arrive avec la fonctionnalité dont il dépend.
    earned: Callable | None


def _validated_solutions(user):
    # Une solution générée par IA ne rapporte ni points ni badge.
    return Solution.objects.filter(author=user, status=Solution.Status.VALIDATED).exclude(
        ai_usage=Solution.AiUsage.GENERATED
    )


def _first_step(user):
    return Solution.objects.filter(author=user).exclude(status=Solution.Status.DRAFT).exists()


def _validated(user):
    return _validated_solutions(user).exists()


def _pioneer(user):
    return PointTransaction.objects.filter(
        user=user, reason=PointTransaction.Reason.FIRST_VALIDATED, reversed_by__isnull=True
    ).exists()


def _author(user):
    return (
        Exercise.objects.filter(author=user)
        .annotate(
            solvers=Count(
                "solutions__author",
                filter=Q(solutions__status=Solution.Status.VALIDATED) & ~Q(solutions__author=user),
                distinct=True,
            )
        )
        .filter(solvers__gte=AUTHOR_SOLVERS)
        .exists()
    )


def _reliable_reviewer(user):
    stats = Review.objects.filter(reviewer=user, agrees_with_consensus__isnull=False).aggregate(
        total=Count("pk"), agreed=Count("pk", filter=Q(agrees_with_consensus=True))
    )
    return stats["total"] >= RELIABLE_REVIEWS and stats["agreed"] >= RELIABLE_AGREEMENT * stats["total"]


def _all_rounder(user):
    topics = _validated_solutions(user).values_list("exercise__topics", flat=True)
    return len({topic for topic in topics if topic is not None}) >= ALL_ROUNDER_TOPICS


def _elegance(user):
    # Seuls les votes qui pèsent comptent : pas ceux des comptes de moins de 7 jours.
    return (
        Solution.objects.filter(author=user)
        .annotate(useful=Count("votes", filter=Q(votes__weight__gt=0)))
        .filter(useful__gte=ELEGANCE_VOTES)
        .exists()
    )


def _duplicate_hunter(user):
    return Report.objects.filter(
        reporter=user, reason=Report.Reason.DUPLICATE, status=Report.Status.CONFIRMED
    ).exists()


BADGES = [
    Badge("premier-pas", "Premier pas", "Proposer ta première solution.", _first_step),
    Badge("valide", "Validé !", "Obtenir ta première solution validée par les pairs.", _validated),
    Badge("pionnier", "Pionnier", "Être le premier à résoudre un exercice.", _pioneer),
    Badge(
        "auteur",
        "Auteur",
        f"Publier un exercice résolu par {AUTHOR_SOLVERS} autres membres.",
        _author,
    ),
    Badge(
        "relecteur-fiable",
        "Relecteur fiable",
        f"Rendre {RELIABLE_REVIEWS} relectures, dont au moins {RELIABLE_AGREEMENT * 100:.0f} % "
        "conformes au verdict final.",
        _reliable_reviewer,
    ),
    Badge(
        "touche-a-tout",
        "Touche-à-tout",
        f"Avoir des solutions validées dans {ALL_ROUNDER_TOPICS} chapitres différents.",
        _all_rounder,
    ),
    Badge(
        "elegance",
        "Élégance",
        f"Recevoir {ELEGANCE_VOTES} votes « utile » sur une même solution.",
        _elegance,
    ),
    Badge(
        "chasseur-de-doublons",
        "Chasseur de doublons",
        "Signaler un doublon confirmé par la modération.",
        _duplicate_hunter,
    ),
]
BADGES_BY_SLUG = {badge.slug: badge for badge in BADGES}


def check_badges(user, *, now=None):
    """Attribue les badges que `user` remplit et n'a pas encore. Renvoie les nouveaux."""
    if user is None:
        return []
    owned = set(UserBadge.objects.filter(user=user).values_list("badge", flat=True))
    new = [badge for badge in BADGES if badge.earned and badge.slug not in owned and badge.earned(user)]
    now = now or timezone.now()
    UserBadge.objects.bulk_create(
        [UserBadge(user=user, badge=badge.slug, awarded_at=now) for badge in new],
        ignore_conflicts=True,
    )
    return new
