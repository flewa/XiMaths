"""Comptes liés : détection basique et neutralisation des interactions mutuelles.

Aucune sanction automatique : une classe entière peut partager le même réseau.
On neutralise seulement ce que deux comptes liés font l'un pour l'autre.
"""

from django.db import transaction
from django.db.models import Q

from content.models import Vote
from gamification.models import PointTransaction
from gamification.services import reverse

from .models import AccountLink

# A et B représentent chacun plus de 50 % des votes donnés par l'autre, sur 10 votes au moins.
RECIPROCITY_SHARE = 0.5
RECIPROCITY_MIN_VOTES = 10


def linked_ids(user_or_id):
    """Identifiants des comptes liés à ce compte."""
    pk = getattr(user_or_id, "pk", user_or_id)
    if pk is None:
        return set()
    pairs = AccountLink.objects.filter(Q(user_a_id=pk) | Q(user_b_id=pk)).values_list(
        "user_a_id", "user_b_id"
    )
    return {other for pair in pairs for other in pair} - {pk}


def are_linked(first, second):
    if first is None or second is None:
        return False
    return getattr(second, "pk", second) in linked_ids(first)


def _votes_between(voter_id, author_id):
    return Vote.objects.filter(voter_id=voter_id).filter(
        Q(exercise__author_id=author_id) | Q(solution__author_id=author_id)
    )


def _share_towards(voter_id, author_id):
    """(part des votes de `voter` qui vont à `author`, nombre de votes de `voter`)."""
    cast = Vote.objects.filter(voter_id=voter_id).count()
    if cast == 0:
        return 0.0, 0
    return _votes_between(voter_id, author_id).count() / cast, cast


@transaction.atomic
def link_accounts(first, second, link_type, *, strength=1.0, confirmed_by=None):
    """Lie deux comptes et neutralise leurs votes mutuels : poids 0, points annulés."""
    link, created = AccountLink.objects.get_or_create(
        user_a_id=min(first.pk, second.pk),
        user_b_id=max(first.pk, second.pk),
        link_type=link_type,
        defaults={"strength": strength, "confirmed_by": confirmed_by},
    )
    mutual = _votes_between(first.pk, second.pk) | _votes_between(second.pk, first.pk)
    vote_ids = list(mutual.values_list("pk", flat=True))
    for txn in PointTransaction.objects.filter(
        source_type="content.vote", source_id__in=vote_ids, reversed_by__isnull=True
    ).exclude(reason=PointTransaction.Reason.REVERSAL):
        reverse(txn)
    Vote.objects.filter(pk__in=vote_ids).update(weight=0)
    return link, created


def check_vote_reciprocity(voter, author):
    """Appelé après chaque vote : lie les deux comptes si chacun réserve plus de la
    moitié de ses votes à l'autre."""
    if author is None or voter.pk == author.pk:
        return None
    forward, cast_forward = _share_towards(voter.pk, author.pk)
    backward, cast_backward = _share_towards(author.pk, voter.pk)
    if (
        min(cast_forward, cast_backward) >= RECIPROCITY_MIN_VOTES
        and forward > RECIPROCITY_SHARE
        and backward > RECIPROCITY_SHARE
    ):
        link, _ = link_accounts(
            voter, author, AccountLink.LinkType.VOTE_RECIPROCITY, strength=min(forward, backward)
        )
        return link
    return None
