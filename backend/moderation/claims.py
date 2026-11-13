"""Prise en charge des dossiers de modération : « Je m'en occupe ».

Deux modérateurs qui ouvrent le même signalement en même temps le liraient deux fois, et
le second tomberait sur « déjà tranché ». Une prise en charge le montre aux collègues. Ce
n'est qu'une indication : elle n'empêche personne de trancher, expire au bout de deux heures
et disparaît avec la décision.
"""

import re
from datetime import timedelta

from django.utils import timezone

from config.errors import RuleError

from .models import ModerationClaim

CLAIM_TTL = timedelta(hours=2)
KEY = re.compile(r"^(report|message|appeal):\d{1,12}$")


def valid_key(key):
    return bool(KEY.match(key))


def _fresh(now=None):
    now = now or timezone.now()
    return ModerationClaim.objects.filter(claimed_at__gt=now - CLAIM_TTL).select_related("moderator")


def current(keys, now=None):
    """Prises en charge en cours, par clé de dossier."""
    return {claim.key: claim for claim in _fresh(now).filter(key__in=list(keys))}


def claim_out(claim, me):
    if claim is None:
        return None
    return {"username": claim.moderator.username, "since": claim.claimed_at, "mine": claim.moderator_id == me.pk}


def take(key, moderator, *, take_over=False, now=None):
    """Prend le dossier. Déjà pris par un collègue : refus, sauf à prendre le relais."""
    now = now or timezone.now()
    if not valid_key(key):
        raise RuleError("Dossier inconnu.")
    held = current([key], now).get(key)
    if held and held.moderator_id != moderator.pk and not take_over:
        raise RuleError(f"{held.moderator.username} s'en occupe déjà.")
    claim, _ = ModerationClaim.objects.update_or_create(
        key=key, defaults={"moderator": moderator, "claimed_at": now}
    )
    return claim


def release(key, moderator):
    """Rend le dossier : seulement le sien."""
    ModerationClaim.objects.filter(key=key, moderator=moderator).delete()


def settle(key):
    """Le dossier est tranché : la prise en charge n'a plus lieu d'être."""
    ModerationClaim.objects.filter(key=key).delete()
