"""Détection des doublons : empreintes, candidats, bandes, publication et arbitrage.

Les seuils sont les valeurs de départ du document de conception, à calibrer sur
les décisions humaines. Aucune fusion n'est automatique : l'auteur garde la main
au moment de publier, et un modérateur tranche ensuite.
"""

from dataclasses import dataclass

import numpy as np
from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone
from pgvector.django import CosineDistance

from accounts.permissions import is_moderator
from config.errors import RuleError
from content.models import Exercise, Solution
from content.services import publish_exercise
from notifications.models import Notification
from notifications.services import notify

from .embeddings import embed
from .minhash import lsh_keys, signature, similarity
from .models import DuplicatePair, Fingerprint, LshKey
from .normalize import normalize
from .signals import pair_decided

Band = DuplicatePair.Band
Status = DuplicatePair.Status
Choice = DuplicatePair.AuthorChoice

# À incrémenter quand la normalisation change : scan_duplicates --reindex.
NORMALIZATION_VERSION = 1
QUASI_COPY_JACCARD = 0.85
VARIANT_JACCARD = 0.85
VERY_SIMILAR_SCORE = 0.88
MAYBE_RELATED_SCORE = 0.80
EMBEDDING_NEIGHBOURS = 20
# s = 0,45 cos(E1) + 0,35 cos(E2) + 0,20 J(F). E2, l'embedding du résumé canonique
# écrit par un LLM, n'existe que si un LLM est configuré, et seulement pour les énoncés
# publiés (le résumé est calculé par la tâche nocturne, pas pendant la rédaction).
# Sans lui, cos(E1) tient sa place : renormaliser les deux autres poids donnerait à E1
# seul un maximum de 0,69, sous tous les seuils.
WEIGHT_E1 = 0.45
WEIGHT_E2 = 0.35
WEIGHT_F = 0.20
# Bandes qui affichent l'écran « Cet exercice existe peut-être déjà » à la publication.
CONFIRM_BANDS = (Band.QUASI_COPY, Band.VERY_SIMILAR, Band.VARIANT)
BAND_ORDER = [Band.QUASI_COPY, Band.VERY_SIMILAR, Band.VARIANT, Band.MAYBE_RELATED]


@dataclass(frozen=True)
class Prints:
    canonical: str
    signature: list[int]
    abstract_signature: list[int]
    embedding: list[float] | None
    summary_embedding: list[float] | None = None


@dataclass(frozen=True)
class Match:
    exercise: Exercise
    band: str
    jaccard: float
    abstract_jaccard: float
    cosine: float | None
    score: float | None


class DuplicateSuspected(Exception):
    """Un exercice publié est proche : l'auteur doit dire ce qu'il en est."""

    def __init__(self, matches):
        super().__init__("Cet exercice existe peut-être déjà.")
        self.matches = matches


def compute_prints(statement):
    normalized = normalize(statement)
    return Prints(
        canonical=normalized.canonical,
        signature=signature(normalized.alpha),
        abstract_signature=signature(normalized.abstract),
        embedding=embed(normalized.canonical),
    )


def _stored_prints(fingerprint):
    return Prints(
        canonical=fingerprint.canonical,
        signature=fingerprint.signature,
        abstract_signature=fingerprint.abstract_signature,
        embedding=None if fingerprint.embedding is None else list(fingerprint.embedding),
        summary_embedding=None if fingerprint.summary_embedding is None else list(fingerprint.summary_embedding),
    )


@transaction.atomic
def index_exercise(exercise, prints=None):
    prints = prints or compute_prints(exercise.statement)
    defaults = {
        "version": NORMALIZATION_VERSION,
        "canonical": prints.canonical,
        "signature": prints.signature,
        "abstract_signature": prints.abstract_signature,
        "embedding": prints.embedding,
    }
    # Énoncé modifié : son résumé canonique (E2) est à refaire.
    if not Fingerprint.objects.filter(exercise=exercise, canonical=prints.canonical).exists():
        defaults |= {"summary": "", "summary_embedding": None}
    fingerprint, _ = Fingerprint.objects.update_or_create(exercise=exercise, defaults=defaults)
    fingerprint.lsh_keys.all().delete()
    LshKey.objects.bulk_create(
        [LshKey(fingerprint=fingerprint, kind=LshKey.Kind.ALPHA, key=key) for key in lsh_keys(prints.signature)]
        + [
            LshKey(fingerprint=fingerprint, kind=LshKey.Kind.ABSTRACT, key=key)
            for key in lsh_keys(prints.abstract_signature)
        ]
    )
    return fingerprint


def classify(jaccard, abstract_jaccard, score):
    """Bande d'une paire, ou None si les exercices sont distincts."""
    # Seules les constantes changent : variante, même si le reste de l'énoncé est
    # identique (un long énoncé dont une valeur change garde un J(F) élevé).
    if abstract_jaccard == 1 and jaccard < 1:
        return Band.VARIANT
    if jaccard >= QUASI_COPY_JACCARD:
        return Band.QUASI_COPY
    # Avant « très similaire » : Σ 1/n² et Σ 1/n ont des embeddings presque
    # identiques, mais la version abstraite montre qu'ils diffèrent par une constante.
    if abstract_jaccard >= VARIANT_JACCARD:
        return Band.VARIANT
    if score is not None and score >= VERY_SIMILAR_SCORE:
        return Band.VERY_SIMILAR
    if score is not None and score >= MAYBE_RELATED_SCORE:
        return Band.MAYBE_RELATED
    return None


def _nearest_by_embedding(vector, k=EMBEDDING_NEIGHBOURS, field="embedding"):
    indexed = Fingerprint.objects.filter(
        **{f"{field}__isnull": False}, exercise__status=Exercise.Status.PUBLISHED
    )
    if connection.vendor == "postgresql":
        return list(
            indexed.order_by(CosineDistance(field, vector)).values_list("pk", flat=True)[:k]
        )
    # SQLite (développement et tests) : parcours complet, suffisant pour quelques milliers d'énoncés.
    rows = list(indexed.values_list("pk", field))
    rows.sort(key=lambda row: -float(np.dot(vector, row[1])))
    return [pk for pk, _ in rows[:k]]


def _declared_distinct(exercise):
    pairs = DuplicatePair.objects.filter(
        Q(exercise=exercise) | Q(existing=exercise), status=Status.DISTINCT
    ).values_list("exercise_id", "existing_id")
    return {pk for pair in pairs for pk in pair} - {exercise.pk}


def find_similar(prints, *, exercise=None, limit=5):
    """Exercices publiés proches d'un énoncé, du plus proche au moins proche.

    Candidats : collisions LSH sur F et F′, et les 20 plus proches voisins sur E1 et
    sur E2. Une paire déclarée distincte n'est jamais reproposée."""
    candidates = set(
        LshKey.objects.filter(
            Q(kind=LshKey.Kind.ALPHA, key__in=lsh_keys(prints.signature))
            | Q(kind=LshKey.Kind.ABSTRACT, key__in=lsh_keys(prints.abstract_signature))
        ).values_list("fingerprint_id", flat=True)
    )
    if prints.embedding is not None:
        candidates |= set(_nearest_by_embedding(prints.embedding))
    if prints.summary_embedding is not None:
        candidates |= set(_nearest_by_embedding(prints.summary_embedding, field="summary_embedding"))
    if exercise is not None:
        candidates -= {exercise.pk} | _declared_distinct(exercise)

    matches = []
    for fingerprint in Fingerprint.objects.filter(
        pk__in=candidates, exercise__status=Exercise.Status.PUBLISHED
    ).select_related("exercise"):
        jaccard = similarity(prints.signature, fingerprint.signature)
        abstract_jaccard = similarity(prints.abstract_signature, fingerprint.abstract_signature)
        cosine = score = None
        if prints.embedding is not None and fingerprint.embedding is not None:
            cosine = float(np.dot(prints.embedding, fingerprint.embedding))
            if prints.summary_embedding is not None and fingerprint.summary_embedding is not None:
                summary_cosine = float(np.dot(prints.summary_embedding, fingerprint.summary_embedding))
                score = WEIGHT_E1 * cosine + WEIGHT_E2 * summary_cosine + WEIGHT_F * jaccard
            else:
                score = (WEIGHT_E1 + WEIGHT_E2) * cosine + WEIGHT_F * jaccard
        band = classify(jaccard, abstract_jaccard, score)
        if band:
            matches.append(
                Match(fingerprint.exercise, band, jaccard, abstract_jaccard, cosine, score)
            )
    matches.sort(key=lambda m: (BAND_ORDER.index(m.band), -(m.score or m.jaccard)))
    return matches[:limit]


def _record(exercise, match, **fields):
    return DuplicatePair.objects.create(
        exercise=exercise,
        existing=match.exercise,
        band=match.band,
        score=match.score,
        jaccard=match.jaccard,
        abstract_jaccard=match.abstract_jaccard,
        cosine=match.cosine,
        **fields,
    )


@transaction.atomic
def publish_checked(exercise, *, choice="", target_id=None, note="", now=None):
    """Publie un brouillon après la vérification des doublons.

    Si un exercice publié est proche (quasi-copie, très similaire ou variante) et que
    l'auteur n'a pas encore choisi, lève DuplicateSuspected. Sinon :
    - « variante » : publie en lien avec l'exercice choisi ;
    - « différent » : publie, et les paires partent en file d'arbitrage, sans pénalité.
    « C'est le même » ne publie rien : le front renvoie vers l'exercice existant."""
    if exercise.status != Exercise.Status.DRAFT:
        raise RuleError("Seul un brouillon peut être publié.")
    prints = compute_prints(exercise.statement)
    matches = find_similar(prints, exercise=exercise)
    close = [m for m in matches if m.band in CONFIRM_BANDS]
    if close and not choice:
        raise DuplicateSuspected(close)
    target = None
    if choice == Choice.VARIANT:
        target = next((m for m in matches if m.exercise.pk == target_id), None)
        if target is None:
            raise RuleError("Choisis l'exercice dont celui-ci est une variante.")

    publish_exercise(exercise, now=now)
    index_exercise(exercise, prints)
    if target:
        _record(exercise, target, author_choice=Choice.VARIANT, status=Status.VARIANTS)
    elif choice == Choice.DIFFERENT:
        for match in close:
            _record(exercise, match, author_choice=Choice.DIFFERENT, author_note=note)
    return exercise


def scan(exercises):
    """Compare des exercices publiés au stock, et ouvre les paires à arbitrer qui
    n'existent pas encore. Renvoie le nombre de paires ouvertes."""
    opened = 0
    for exercise in exercises:
        fingerprint = getattr(exercise, "fingerprint", None) or index_exercise(exercise)
        for match in find_similar(_stored_prints(fingerprint), exercise=exercise, limit=20):
            if match.band not in CONFIRM_BANDS:
                continue
            older, newer = sorted(
                [exercise, match.exercise], key=lambda e: (e.published_at, e.pk)
            )
            if DuplicatePair.objects.filter(
                Q(exercise=older, existing=newer) | Q(exercise=newer, existing=older)
            ).exists():
                continue
            _record(newer, match if newer == exercise else _swap(match, exercise))
            opened += 1
    return opened


def _swap(match, exercise):
    """La même paire, vue depuis l'autre exercice."""
    return Match(exercise, match.band, match.jaccard, match.abstract_jaccard, match.cosine, match.score)


def variants_of(exercise):
    """Exercices liés comme variantes, publiés."""
    pairs = DuplicatePair.objects.filter(
        Q(exercise=exercise) | Q(existing=exercise), status=Status.VARIANTS
    ).values_list("exercise_id", "existing_id")
    ids = {pk for pair in pairs for pk in pair} - {exercise.pk}
    return Exercise.objects.filter(pk__in=ids, status=Exercise.Status.PUBLISHED).order_by("published_at")


# ---------------------------------------------------------------- arbitrage


def _check_moderator(user):
    if not is_moderator(user):
        raise PermissionDenied("Seuls les modérateurs arbitrent les doublons.")


@transaction.atomic
def decide(pair, status, moderator, *, now=None):
    """Tranche une paire : fusionner, lier comme variantes ou déclarer distincts."""
    _check_moderator(moderator)
    if pair.status == Status.MERGED:
        raise RuleError("Annule d'abord la fusion.")
    if status == Status.MERGED:
        _merge(pair)
    pair.status = status
    pair.decided_by = moderator
    pair.decided_at = now or timezone.now()
    pair.save()
    pair_decided.send(sender=DuplicatePair, pair=pair, moderator=moderator)
    return pair


def open_reported_pair(first, second):
    """Paire à arbitrer pour un doublon signalé par un membre : l'existante si elle
    attend déjà, sinon une nouvelle. Refuse une paire déjà tranchée."""
    existing = DuplicatePair.objects.filter(
        Q(exercise=first, existing=second) | Q(exercise=second, existing=first)
    ).first()
    if existing is not None:
        if existing.status == Status.DISTINCT:
            raise RuleError("La modération a déjà jugé ces deux exercices distincts.")
        if existing.status != Status.PENDING:
            raise RuleError("Ces deux exercices sont déjà fusionnés ou liés comme variantes.")
        return existing
    older, newer = sorted([first, second], key=lambda e: (e.published_at, e.pk))
    prints = [getattr(exercise, "fingerprint", None) for exercise in (newer, older)]
    jaccard = abstract_jaccard = 0.0
    cosine = None
    if all(prints):
        jaccard = similarity(prints[0].signature, prints[1].signature)
        abstract_jaccard = similarity(prints[0].abstract_signature, prints[1].abstract_signature)
        if prints[0].embedding is not None and prints[1].embedding is not None:
            cosine = float(np.dot(prints[0].embedding, prints[1].embedding))
    return DuplicatePair.objects.create(
        exercise=newer,
        existing=older,
        band=Band.REPORTED,
        jaccard=jaccard,
        abstract_jaccard=abstract_jaccard,
        cosine=cosine,
        score=None if cosine is None else WEIGHT_E1 * cosine + WEIGHT_F * jaccard,
    )


def _merge(pair):
    """Le plus récent rejoint le plus ancien : ses solutions passent sur l'exercice
    canonique, son adresse redirige, et son auteur garde ses points."""
    merged, canonical = pair.exercise, pair.existing
    if {merged.status, canonical.status} != {Exercise.Status.PUBLISHED}:
        raise RuleError("Les deux exercices doivent être publiés pour être fusionnés.")
    solutions = Solution.objects.filter(exercise=merged)
    pair.moved_solutions = list(solutions.values_list("pk", flat=True))
    solutions.update(exercise=canonical)
    merged.status = Exercise.Status.MERGED
    merged.merged_into = canonical
    merged.save(update_fields=["status", "merged_into", "updated_at"])
    notify(
        merged.author,
        Notification.Kind.DUPLICATE_MERGED,
        "Ton exercice a été regroupé avec un exercice existant",
        f"« {merged.title} » rejoint « {canonical.title} ». Tu gardes tes points, et ses solutions "
        "sont désormais sur l'exercice d'origine.",
        f"/exercices/{canonical.pk}",
    )


@transaction.atomic
def unmerge(pair, moderator):
    """Annule une fusion : la paire revient dans la file d'arbitrage, sans décision."""
    _check_moderator(moderator)
    if pair.status != Status.MERGED:
        raise RuleError("Cette paire n'est pas fusionnée.")
    Solution.objects.filter(pk__in=pair.moved_solutions).update(exercise=pair.exercise)
    merged = pair.exercise
    merged.status = Exercise.Status.PUBLISHED
    merged.merged_into = None
    merged.save(update_fields=["status", "merged_into", "updated_at"])
    pair.status = Status.PENDING
    pair.moved_solutions = []
    pair.decided_by = None
    pair.decided_at = None
    pair.save()
    return pair
