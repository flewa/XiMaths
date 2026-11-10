"""Copie modèle d'un exercice. Les copies sont privées ; celle-ci fait exception, à trois
conditions : son auteur a donné son accord, l'équipe du site l'a choisie parmi les copies
validées, et celui qui la lit a d'abord envoyé la sienne. Elle est montrée sans nom. Qui
l'ouvre peut encore envoyer une copie, mais elle ne rapporte plus de points."""

from datetime import datetime

from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth

from accounts.permissions import is_moderator

from . import photos
from .api import MySolutionOut, PhotoOut
from .models import Exercise, ModelCopyView, Solution
from .services import can_open_model_copy, choose_model_copy, model_candidates, model_copy, set_model_consent

router = Router(tags=["copie modèle"])


class ModelCopyOut(Schema):
    # Une copie modèle existe pour cet exercice.
    exists: bool
    # Le membre peut l'ouvrir : il a envoyé sa copie (ou c'est l'auteur de l'exercice, ou l'équipe).
    can_open: bool
    opened: bool
    # Ouvrir la copie modèle privera de points une prochaine copie : faux pour qui a déjà une copie validée.
    costs_points: bool
    photos: list[PhotoOut]


class CandidateOut(Schema):
    id: int
    photos: list[PhotoOut]
    validated_at: datetime | None
    is_model: bool


class ConsentIn(Schema):
    consent: bool


class ChoiceIn(Schema):
    chosen: bool


def published(exercise_id):
    return get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)


def describe(exercise, user):
    model = model_copy(exercise)
    can_open = model is not None and can_open_model_copy(user, exercise)
    opened = can_open and ModelCopyView.objects.filter(exercise=exercise, user=user).exists()
    validated = (
        user.is_authenticated
        and Solution.objects.filter(exercise=exercise, author=user, status=Solution.Status.VALIDATED).exists()
    )
    return {
        "exists": model is not None,
        "can_open": can_open,
        "opened": opened,
        "costs_points": bool(can_open and not opened and not validated and exercise.author_id != user.pk),
        "photos": photos.described(model) if opened else [],
    }


@router.get("/exercises/{int:exercise_id}/model-copy", response=ModelCopyOut)
def get_model_copy(request, exercise_id: int):
    return describe(published(exercise_id), request.user)


@router.post("/exercises/{int:exercise_id}/model-copy/open", response=ModelCopyOut, auth=django_auth)
def open_model_copy(request, exercise_id: int):
    """Ouvre la copie modèle, et le note : les copies suivantes du membre sur cet exercice
    ne rapporteront plus de points."""
    exercise = published(exercise_id)
    if model_copy(exercise) is None:
        raise HttpError(404, "Pas de copie modèle pour cet exercice.")
    if not can_open_model_copy(request.auth, exercise):
        raise HttpError(403, "Envoie d'abord ta copie : la copie modèle se débloque ensuite.")
    ModelCopyView.objects.get_or_create(exercise=exercise, user=request.auth)
    return describe(exercise, request.auth)


@router.post("/solutions/{int:solution_id}/model-consent", response=MySolutionOut, auth=django_auth)
def model_consent(request, solution_id: int, payload: ConsentIn):
    """L'auteur donne ou retire son accord. Retiré, sa copie cesse aussitôt d'être le modèle."""
    solution = get_object_or_404(Solution, pk=solution_id, author=request.auth)
    return set_model_consent(solution, payload.consent)


@router.get("/exercises/{int:exercise_id}/model-candidates", response=list[CandidateOut], auth=django_auth)
def candidates(request, exercise_id: int):
    """Pour l'équipe : les copies validées dont l'auteur accepte qu'elles servent de modèle."""
    if not is_moderator(request.auth):
        raise HttpError(403, "Réservé à l'équipe du site.")
    return [
        {
            "id": solution.pk,
            "photos": photos.described(solution),
            "validated_at": solution.validated_at,
            "is_model": solution.model_at is not None,
        }
        for solution in model_candidates(published(exercise_id)).prefetch_related("photos")
    ]


@router.post("/solutions/{int:solution_id}/model", response=list[CandidateOut], auth=django_auth)
def choose(request, solution_id: int, payload: ChoiceIn):
    if not is_moderator(request.auth):
        raise HttpError(403, "Réservé à l'équipe du site.")
    solution = get_object_or_404(Solution.objects.select_related("exercise", "author"), pk=solution_id)
    choose_model_copy(solution, payload.chosen)
    return candidates(request, solution.exercise_id)
