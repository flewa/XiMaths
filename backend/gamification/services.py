"""Écritures dans le ledger des points : crédit idempotent, plafonds, annulations."""

from datetime import datetime, time, timedelta

from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.utils import timezone

from .models import PointTransaction
from .scoring import (
    DAILY_COUNT_CAPS,
    MEMBER_MIN_DAYS,
    MEMBER_MIN_POINTS,
    POINTS,
    UNVALIDATED_DAILY_CAP,
    UNVALIDATED_REASONS,
)

Reason = PointTransaction.Reason


def source_key(obj):
    """Identifie l'objet à l'origine des points : (« app.modèle », pk)."""
    return obj._meta.label_lower, obj.pk


def start_of_day(now=None):
    """Minuit du jour en cours, heure de Paris (TIME_ZONE)."""
    local = timezone.localtime(now)
    return timezone.make_aware(datetime.combine(local.date(), time.min))


def balance(user, *, since=None, level=None):
    qs = PointTransaction.objects.filter(user=user)
    if since is not None:
        qs = qs.filter(created_at__gte=since)
    if level is not None:
        qs = qs.filter(level=level)
    return qs.aggregate(total=Sum("amount"))["total"] or 0


def _capped_amount(user, reason, amount, now):
    """Réduit `amount` selon les plafonds quotidiens ; 0 si un plafond est atteint."""
    if amount <= 0 or reason not in UNVALIDATED_REASONS:
        return amount
    today = PointTransaction.objects.filter(user=user, created_at__gte=start_of_day(now))
    if today.filter(reason=reason).count() >= DAILY_COUNT_CAPS[reason]:
        return 0
    spent = (
        today.filter(reason__in=UNVALIDATED_REASONS).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    return max(0, min(amount, UNVALIDATED_DAILY_CAP - spent))


def award(user, reason, source, *, amount=None, level=None, now=None):
    """Crédite (ou débite) des points pour `source`.

    Idempotent : une même source ne rapporte qu'une fois par motif, et un
    second appel renvoie l'écriture existante. Renvoie None si un plafond
    ramène le montant à zéro.
    """
    now = now or timezone.now()
    source_type, source_id = source_key(source)
    lookup = {"user": user, "reason": reason, "source_type": source_type, "source_id": source_id}
    existing = PointTransaction.objects.filter(**lookup).first()
    if existing:
        return existing

    amount = POINTS[reason] if amount is None else amount
    amount = _capped_amount(user, reason, amount, now)
    if amount == 0:
        return None
    try:
        with transaction.atomic():
            txn = PointTransaction.objects.create(
                **lookup, amount=amount, level=level, created_at=now
            )
    except IntegrityError:
        # Une écriture concurrente pour la même source a gagné la course.
        return PointTransaction.objects.get(**lookup)
    if amount > 0:
        promote_new_member(user, now=now)
    return txn


def promote_new_member(user, *, now=None):
    """Nouveau → Membre dès 7 jours d'ancienneté et 30 points. Les niveaux
    suivants restent attribués à la main pour l'instant."""
    now = now or timezone.now()
    if (
        user.trust_level == user.TrustLevel.NEW
        and user.date_joined <= now - timedelta(days=MEMBER_MIN_DAYS)
        and balance(user) >= MEMBER_MIN_POINTS
    ):
        user.trust_level = user.TrustLevel.MEMBER
        user.save(update_fields=["trust_level"])
        return True
    return False


def reverse(txn, *, now=None):
    """Annule une écriture par l'écriture opposée. Idempotent."""
    if txn.reason == Reason.REVERSAL:
        raise ValueError("On n'annule pas une annulation.")
    existing = PointTransaction.objects.filter(reverses=txn).first()
    if existing:
        return existing
    source_type, source_id = source_key(txn)
    return PointTransaction.objects.create(
        user=txn.user,
        amount=-txn.amount,
        reason=Reason.REVERSAL,
        source_type=source_type,
        source_id=source_id,
        level=txn.level,
        reverses=txn,
        created_at=now or timezone.now(),
    )


def points_from(user, reason, sources):
    """Total déjà crédité à `user` pour `reason` depuis ces objets (pour les plafonds par cible)."""
    sources = list(sources)
    if not sources:
        return 0
    source_type = sources[0]._meta.label_lower
    return (
        PointTransaction.objects.filter(
            user=user,
            reason=reason,
            source_type=source_type,
            source_id__in=[s.pk for s in sources],
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )


@transaction.atomic
def reverse_points_from(target, *, now=None):
    """Annule les points nés d'un exercice ou d'une solution retirés : ceux de la
    publication, des votes reçus et, pour une solution, de sa validation (y compris
    les +3 de l'auteur de l'exercice). Pour un exercice, son auteur perd aussi les
    +3 reçus par solution ; les solveurs, de bonne foi, gardent les leurs."""
    source_type, source_id = source_key(target)
    vote_ids = list(target.votes.values_list("pk", flat=True))
    earned = Q(source_type=source_type, source_id=source_id) | Q(
        source_type="content.vote", source_id__in=vote_ids
    )
    if source_type == "content.exercise" and target.author_id:
        earned |= Q(
            user_id=target.author_id,
            reason=Reason.EXERCISE_SOLVED,
            source_type="content.solution",
            source_id__in=list(target.solutions.values_list("pk", flat=True)),
        )
    transactions = (
        PointTransaction.objects.filter(earned)
        .exclude(reason__in=[Reason.REVERSAL, Reason.PLAGIARISM_PENALTY])
        .filter(reversed_by__isnull=True)
    )
    return [reverse(txn, now=now) for txn in transactions]


@transaction.atomic
def apply_plagiarism(solution, *, now=None):
    """Plagiat confirmé par un humain : annule tous les points issus de la solution
    (y compris ceux de l'auteur de l'exercice et des votes reçus), puis −50 à l'auteur."""
    reverse_points_from(solution, now=now)
    return award(
        solution.author,
        Reason.PLAGIARISM_PENALTY,
        solution,
        level=solution.exercise.primary_level,
        now=now,
    )
