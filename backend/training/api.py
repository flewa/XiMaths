"""API de l'entraînement chronométré. Toutes les routes sont réservées au titulaire
de la session, et le temps renvoyé est celui du serveur."""

from datetime import datetime
from typing import Literal

from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.security import django_auth
from pydantic import Field

from accounts.permissions import contributor
from content.models import TEXT_MAX_LENGTH, Exercise

from . import services
from .models import TimedSession

router = Router(tags=["entraînement"])


class StartIn(Schema):
    exercise_id: int
    minutes: int


class SaveIn(Schema):
    draft: str = Field(default="", max_length=TEXT_MAX_LENGTH)
    final_answer: str = Field(default="", max_length=200)
    focus_losses: int = Field(default=0, ge=0, le=1000)
    external_paste_chars: int = Field(default=0, ge=0, le=TEXT_MAX_LENGTH)


class SubmitIn(Schema):
    draft: str = Field(default="", max_length=TEXT_MAX_LENGTH)
    final_answer: str = Field(default="", max_length=200)
    ai_usage: Literal["aucune", "relecture", "aide_idee", "generee"] = "aucune"


class RatingIn(Schema):
    rating: int = Field(ge=1, le=5)


class SessionOut(Schema):
    id: int
    exercise_id: int
    exercise_title: str
    statement: str
    hints: list[str]
    has_final_answer: bool
    status: str
    duration_s: int
    extra_time_factor: float
    limit_s: float
    elapsed_s: float
    remaining_s: float
    pauses_left: int
    focus_losses: int
    external_paste_chars: int
    draft: str
    final_answer: str
    answer_correct: bool | None
    solution_id: int | None
    solution_status: str | None
    median_elapsed_s: float | None
    self_rating: int | None
    started_at: datetime
    submitted_at: datetime | None

    @staticmethod
    def resolve_exercise_title(obj):
        return obj.exercise.title

    @staticmethod
    def resolve_statement(obj):
        return obj.exercise.statement

    @staticmethod
    def resolve_hints(obj):
        return obj.exercise.hints

    @staticmethod
    def resolve_has_final_answer(obj):
        return bool(obj.exercise.final_answer.strip())

    @staticmethod
    def resolve_remaining_s(obj):
        return max(services.remaining_s(obj), 0) if obj.open else 0

    @staticmethod
    def resolve_pauses_left(obj):
        return services.MAX_PAUSES - obj.pauses_used

    @staticmethod
    def resolve_solution_status(obj):
        return obj.solution.status if obj.solution else None

    @staticmethod
    def resolve_median_elapsed_s(obj):
        # La comparaison n'a de sens qu'après le rendu.
        if obj.status != TimedSession.Status.SUBMITTED:
            return None
        return services.median_elapsed_s(obj.exercise, exclude=obj)


class OptionsOut(Schema):
    durations: list[int]
    recommended: int
    extra_time_factor: float | None


def _own(request, session_id):
    return get_object_or_404(
        TimedSession.objects.select_related("exercise", "solution"), pk=session_id, user=request.auth
    )


@router.get("/training/options/{int:exercise_id}", response=OptionsOut, auth=django_auth)
def options(request, exercise_id: int):
    """Durées proposées sur l'écran des règles, et tiers-temps appliqué."""
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    return {
        "durations": list(services.DURATIONS_MIN),
        "recommended": services.recommended_minutes(exercise),
        "extra_time_factor": services.EXTRA_TIME_FACTOR if request.auth.tiers_temps else None,
    }


@router.post("/training/sessions", response={201: SessionOut}, auth=django_auth)
def start(request, payload: StartIn):
    """Démarre le chrono, ou reprend la session ouverte sur cet exercice."""
    user = contributor(request)
    exercise = get_object_or_404(Exercise, pk=payload.exercise_id, status=Exercise.Status.PUBLISHED)
    return 201, services.start(user, exercise, minutes=payload.minutes)


@router.get("/training/sessions/{int:session_id}", response=SessionOut, auth=django_auth)
def detail(request, session_id: int):
    return _own(request, session_id)


@router.post("/training/sessions/{int:session_id}/save", response=SessionOut, auth=django_auth)
def save(request, session_id: int, payload: SaveIn):
    """Sauvegarde automatique, toutes les 10 secondes : c'est aussi le signe de vie
    qui fait avancer le chrono."""
    return services.save(_own(request, session_id), **payload.dict())


@router.post("/training/sessions/{int:session_id}/pause", response=SessionOut, auth=django_auth)
def pause(request, session_id: int):
    return services.pause(_own(request, session_id))


@router.post("/training/sessions/{int:session_id}/resume", response=SessionOut, auth=django_auth)
def resume(request, session_id: int):
    return services.resume(_own(request, session_id))


@router.post("/training/sessions/{int:session_id}/submit", response=SessionOut, auth=django_auth)
def submit(request, session_id: int, payload: SubmitIn):
    """Rend la session : réponse vérifiée, justification envoyée en relecture."""
    contributor(request)
    return services.submit(_own(request, session_id), **payload.dict())


@router.post("/training/sessions/{int:session_id}/abandon", response=SessionOut, auth=django_auth)
def abandon(request, session_id: int):
    return services.abandon(_own(request, session_id))


@router.post("/training/sessions/{int:session_id}/rating", response=SessionOut, auth=django_auth)
def rating(request, session_id: int, payload: RatingIn):
    return services.rate(_own(request, session_id), payload.rating)
