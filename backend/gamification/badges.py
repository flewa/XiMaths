"""Badges du MVP : publics, critères affichés, aucun badge secret.

check_badges est appelé après chaque événement qui peut en débloquer un, et
chaque nuit par refresh_progress en filet de sécurité. Un badge obtenu reste acquis.
"""

from collections.abc import Callable
from dataclasses import dataclass

from django.db.models import Count, Q
from django.utils import timezone

from catalog.models import Topic
from content.models import Exercise, Review, Solution
from moderation.models import Report
from notifications.models import Notification
from notifications.services import notify
from training.models import TimedSession

from .models import PointTransaction, UserBadge, WeeklyStreak

AUTHOR_SOLVERS = 5
RELIABLE_REVIEWS = 25
RELIABLE_AGREEMENT = 0.85
ALL_ROUNDER_TOPICS = 5
ELEGANCE_VOTES = 20
UNDER_PRESSURE_CHALLENGES = 5
REGULAR_WEEKS = {"bronze": 4, "argent": 12, "or": 30}


@dataclass(frozen=True)
class Badge:
    slug: str
    name: str
    criterion: str
    # None : le badge arrive avec la fonctionnalité dont il dépend.
    earned: Callable | None
    # Où en est le membre : (fait, objectif). None pour un badge qui ne se mesure pas
    # (pionnier, doublon, adresse académique) : il s'obtient d'un coup.
    progress: Callable | None = None


def _validated_solutions(user):
    # Une solution générée par IA ne rapporte ni points ni badge.
    return Solution.objects.filter(author=user, status=Solution.Status.VALIDATED).exclude(
        ai_usage=Solution.AiUsage.GENERATED
    )


def _sent_solutions(user):
    return Solution.objects.filter(author=user).exclude(status=Solution.Status.DRAFT)


def _first_step(user):
    return _sent_solutions(user).exists()


def _validated(user):
    return _validated_solutions(user).exists()


def _up_to(target, count):
    """Progression vers `target` : (compte plafonné, objectif)."""

    def progress(user):
        return min(count(user), target), target

    return progress


def _pioneer(user):
    return PointTransaction.objects.filter(
        user=user, reason=PointTransaction.Reason.FIRST_VALIDATED, reversed_by__isnull=True
    ).exists()


def _best_solvers(user):
    """Le plus grand nombre de membres qui ont résolu un même exercice de `user`."""
    return (
        Exercise.objects.filter(author=user)
        .annotate(
            solvers=Count(
                "solutions__author",
                filter=Q(solutions__status=Solution.Status.VALIDATED) & ~Q(solutions__author=user),
                distinct=True,
            )
        )
        .order_by("-solvers")
        .values_list("solvers", flat=True)
        .first()
        or 0
    )


def _author(user):
    return _best_solvers(user) >= AUTHOR_SOLVERS


def _reliable_reviewer(user):
    stats = Review.objects.filter(reviewer=user, agrees_with_consensus__isnull=False).aggregate(
        total=Count("pk"), agreed=Count("pk", filter=Q(agrees_with_consensus=True))
    )
    return stats["total"] >= RELIABLE_REVIEWS and stats["agreed"] >= RELIABLE_AGREEMENT * stats["total"]


def _reviews_judged(user):
    """Relectures dont le verdict final est connu (comparées au consensus)."""
    return Review.objects.filter(reviewer=user, agrees_with_consensus__isnull=False).count()


def _validated_topics(user):
    """Chapitres où `user` a une solution validée ; les notions (sous-chapitres) n'en font
    pas de nouveaux."""
    topics = set(_validated_solutions(user).values_list("exercise__topics", flat=True)) - {None}
    return Topic.objects.filter(pk__in=topics, parent=None).count()


def _all_rounder(user):
    return _validated_topics(user) >= ALL_ROUNDER_TOPICS


def _best_useful_votes(user):
    # Les solutions étant privées, on vote pour les exercices. Seuls les votes qui pèsent
    # comptent : pas ceux des comptes de moins de 7 jours.
    return (
        Exercise.objects.filter(author=user, status=Exercise.Status.PUBLISHED)
        .annotate(useful=Count("votes", filter=Q(votes__weight__gt=0)))
        .order_by("-useful")
        .values_list("useful", flat=True)
        .first()
        or 0
    )


def _elegance(user):
    return _best_useful_votes(user) >= ELEGANCE_VOTES


def _duplicate_hunter(user):
    return Report.objects.filter(
        reporter=user, reason=Report.Reason.DUPLICATE, status=Report.Status.CONFIRMED
    ).exists()


def _challenges_validated(user):
    return TimedSession.objects.filter(
        user=user, challenge__isnull=False, solution__status=Solution.Status.VALIDATED
    ).count()


def _under_pressure(user):
    return _challenges_validated(user) >= UNDER_PRESSURE_CHALLENGES


def _verified_student(user):
    return user.academic_verified_at is not None


def _weeks_achieved(user):
    return WeeklyStreak.objects.filter(user=user, status=WeeklyStreak.Status.ACHIEVED).count()


def _regular(weeks):
    def earned(user):
        return _weeks_achieved(user) >= weeks

    return earned


BADGES = [
    Badge(
        "premier-pas",
        "Premier pas",
        "Proposer ta première solution.",
        _first_step,
        _up_to(1, lambda user: _sent_solutions(user).count()),
    ),
    Badge(
        "valide",
        "Validé !",
        "Obtenir ta première solution validée par les pairs.",
        _validated,
        _up_to(1, lambda user: _validated_solutions(user).count()),
    ),
    Badge("pionnier", "Pionnier", "Être le premier à résoudre un exercice.", _pioneer),
    Badge(
        "auteur",
        "Auteur",
        f"Publier un exercice résolu par {AUTHOR_SOLVERS} autres membres.",
        _author,
        _up_to(AUTHOR_SOLVERS, _best_solvers),
    ),
    Badge(
        "relecteur-fiable",
        "Relecteur fiable",
        f"Rendre {RELIABLE_REVIEWS} relectures, dont au moins {RELIABLE_AGREEMENT * 100:.0f}\u00a0% "
        "conformes au verdict final.",
        _reliable_reviewer,
        _up_to(RELIABLE_REVIEWS, _reviews_judged),
    ),
    Badge(
        "touche-a-tout",
        "Touche-à-tout",
        f"Avoir des solutions validées dans {ALL_ROUNDER_TOPICS} chapitres différents.",
        _all_rounder,
        _up_to(ALL_ROUNDER_TOPICS, _validated_topics),
    ),
    Badge(
        "elegance",
        "Élégance",
        f"Publier un exercice qui reçoit {ELEGANCE_VOTES} votes «\u00a0utile\u00a0».",
        _elegance,
        _up_to(ELEGANCE_VOTES, _best_useful_votes),
    ),
    Badge(
        "chasseur-de-doublons",
        "Chasseur de doublons",
        "Signaler un doublon confirmé par la modération.",
        _duplicate_hunter,
    ),
    Badge(
        "sous-pression",
        "Sous pression",
        f"Faire valider la justification de {UNDER_PRESSURE_CHALLENGES} défis du jour.",
        _under_pressure,
        _up_to(UNDER_PRESSURE_CHALLENGES, _challenges_validated),
    ),
    Badge(
        "etudiant-verifie",
        "Étudiant vérifié",
        "Confirmer une adresse email académique, depuis tes réglages.",
        _verified_student,
    ),
    *(
        Badge(
            f"regulier-{tier}",
            f"Régulier · {tier}",
            f"Atteindre ton objectif hebdomadaire {weeks} semaines.",
            _regular(weeks),
            _up_to(weeks, _weeks_achieved),
        )
        for tier, weeks in REGULAR_WEEKS.items()
    ),
]
BADGES_BY_SLUG = {badge.slug: badge for badge in BADGES}


def next_badges(user, *, limit=3):
    """Badges pas encore obtenus qui se mesurent, les plus avancés d'abord ; d'une série à
    paliers (Régulier), seulement le prochain palier. [(badge, fait, objectif)]"""
    owned = set(UserBadge.objects.filter(user=user).values_list("badge", flat=True))
    candidates, series = [], set()
    for badge in BADGES:
        if badge.slug in owned or badge.earned is None or badge.progress is None:
            continue
        family = badge.slug.split("-")[0] if badge.slug.startswith("regulier-") else badge.slug
        if family in series:
            continue
        series.add(family)
        done, target = badge.progress(user)
        candidates.append((badge, done, target))
    candidates.sort(key=lambda item: (-item[1] / item[2], item[2]))
    return candidates[:limit]


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
    for badge in new:
        notify(
            user,
            Notification.Kind.BADGE,
            f"Nouveau badge : {badge.name}",
            badge.criterion,
            f"/membres/{user.username}",
            now=now,
        )
    return new
