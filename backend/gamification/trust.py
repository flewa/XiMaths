"""Niveaux de confiance automatiques. On ne rétrograde jamais automatiquement, et le
niveau Modérateur reste une nomination du staff.

| Niveau    | Condition                                                         |
| Membre    | 7 jours d'ancienneté et 30 points                                 |
| Relecteur | 300 points, 5 solutions validées, aucune sanction depuis 90 jours |
| Expert    | 1 500 points, 30 relectures concordantes, à 80 % ou plus          |
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone

from content.models import Review, Solution
from moderation.models import Sanction
from notifications.models import Notification
from notifications.services import notify

from .services import balance, promote_new_member

User = get_user_model()
TL = User.TrustLevel

REVIEWER_POINTS = 300
REVIEWER_SOLUTIONS = 5
CLEAN_DAYS = 90
EXPERT_POINTS = 1500
EXPERT_AGREED_REVIEWS = 30
EXPERT_AGREEMENT = 0.8

MESSAGES = {
    TL.REVIEWER: ("Tu es maintenant Relecteur", "Tu peux être tiré au sort pour relire, et signaler des doublons."),
    TL.EXPERT: ("Tu es maintenant Expert", "Tes relectures pèsent 1,5, et tu peux trancher les solutions contestées."),
}


def _reviewer_ready(user, now):
    if balance(user) < REVIEWER_POINTS:
        return False
    validated = (
        Solution.objects.filter(author=user, status=Solution.Status.VALIDATED)
        .exclude(ai_usage=Solution.AiUsage.GENERATED)
        .count()
    )
    recent_sanction = Sanction.objects.filter(user=user, created_at__gte=now - timedelta(days=CLEAN_DAYS)).exists()
    return validated >= REVIEWER_SOLUTIONS and not recent_sanction


def _expert_ready(user):
    if balance(user) < EXPERT_POINTS:
        return False
    stats = Review.objects.filter(reviewer=user, agrees_with_consensus__isnull=False).aggregate(
        total=Count("pk"), agreed=Count("pk", filter=Q(agrees_with_consensus=True))
    )
    return stats["agreed"] >= EXPERT_AGREED_REVIEWS and stats["agreed"] >= EXPERT_AGREEMENT * stats["total"]


def promote(user, *, now=None):
    """Monte d'un ou plusieurs niveaux si les conditions sont remplies. Renvoie le
    nouveau niveau, ou None."""
    if user is None or not user.is_active or user.trust_level >= TL.MODERATOR:
        return None
    now = now or timezone.now()
    start = user.trust_level
    if user.trust_level == TL.NEW:
        promote_new_member(user, now=now)
    if user.trust_level == TL.MEMBER and _reviewer_ready(user, now):
        user.trust_level = TL.REVIEWER
    if user.trust_level == TL.REVIEWER and _expert_ready(user):
        user.trust_level = TL.EXPERT
    if user.trust_level == start:
        return None
    # Le passage à Membre est déjà enregistré et annoncé par promote_new_member.
    if user.trust_level > TL.MEMBER:
        user.save(update_fields=["trust_level"])
        title, body = MESSAGES[user.trust_level]
        notify(user, Notification.Kind.PROMOTION, title, body, "/relectures", now=now)
    return user.trust_level
