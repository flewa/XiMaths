"""API de l'entraînement chronométré et du défi du jour. Les routes de session sont
réservées à leur titulaire, et le temps renvoyé est celui du serveur."""

from datetime import datetime
from typing import Literal

from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema
from ninja.security import django_auth
from pydantic import Field

from accounts.permissions import contributor
from content.models import TEXT_MAX_LENGTH, Exercise

from . import challenges, services
from .models import Challenge, TimedSession

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
    kind: Literal["entrainement", "defi"]
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
    # Défi du jour.
    hint_count: int
    hints_opened: int
    challenge_closes_at: datetime | None
    points_max: int | None
    bonus: float | None
    answer_points: int
    justification_points: int

    @staticmethod
    def resolve_kind(obj):
        return "defi" if obj.ranked else "entrainement"

    @staticmethod
    def resolve_exercise_title(obj):
        return obj.exercise.title

    @staticmethod
    def resolve_statement(obj):
        return challenges.statement(obj)

    @staticmethod
    def resolve_hints(obj):
        # En défi, une indication n'est envoyée qu'une fois ouverte : elle coûte du bonus.
        return obj.exercise.hints[: obj.hints_opened] if obj.ranked else obj.exercise.hints

    @staticmethod
    def resolve_hint_count(obj):
        return len(obj.exercise.hints)

    @staticmethod
    def resolve_challenge_closes_at(obj):
        return obj.challenge.closes_at if obj.ranked else None

    @staticmethod
    def resolve_points_max(obj):
        return round(challenges.points_total(obj.exercise) * (1 + challenges.SPEED_BONUS)) if obj.ranked else None

    @staticmethod
    def resolve_has_final_answer(obj):
        # Un défi a toujours une réponse à vérifier, celle de ses paramètres.
        return obj.ranked or bool(obj.exercise.final_answer.strip())

    @staticmethod
    def resolve_remaining_s(obj):
        return max(services.remaining_s(obj), 0) if obj.open else 0

    @staticmethod
    def resolve_pauses_left(obj):
        return 0 if obj.ranked else services.MAX_PAUSES - obj.pauses_used

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
        TimedSession.objects.select_related("exercise", "solution", "challenge__template"),
        pk=session_id,
        user=request.auth,
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


@router.post("/training/sessions/{int:session_id}/hint", response=SessionOut, auth=django_auth)
def hint(request, session_id: int):
    """Défi : ouvre l'indication suivante, au prix de 10 % du bonus de rapidité."""
    return challenges.open_hint(_own(request, session_id))


# ---------------------------------------------------------------- défi du jour


class MyAttemptOut(Schema):
    session_id: int
    status: str
    answer_correct: bool | None
    answer_points: int
    justification_points: int


class ChallengeOut(Schema):
    id: int
    level: str
    level_name: str
    exercise_title: str
    difficulty: int
    minutes: int
    points_max: int
    closes_at: datetime
    hint_count: int
    attempt: MyAttemptOut | None


def _challenge_out(challenge, attempt):
    exercise = challenge.template.exercise
    return {
        "id": challenge.pk,
        "level": challenge.level.code,
        "level_name": challenge.level.name,
        "exercise_title": exercise.title,
        "difficulty": exercise.difficulty,
        "minutes": challenges.MINUTES,
        "points_max": round(challenges.points_total(exercise) * (1 + challenges.SPEED_BONUS)),
        "closes_at": challenge.closes_at,
        "hint_count": len(exercise.hints),
        "attempt": attempt
        and {
            "session_id": attempt.pk,
            "status": attempt.status,
            "answer_correct": attempt.answer_correct,
            "answer_points": attempt.answer_points,
            "justification_points": attempt.justification_points,
        },
    }


@router.get("/challenges/today", response=list[ChallengeOut])
def today(request):
    """Défis ouverts aujourd'hui, un par niveau. L'énoncé n'est envoyé qu'au départ."""
    now = timezone.now()
    open_challenges = list(challenges.open_today(now))
    attempts = {}
    if request.user.is_authenticated:
        attempts = {
            session.challenge_id: session
            for session in TimedSession.objects.filter(user=request.user, challenge__in=open_challenges)
        }
    return [_challenge_out(challenge, attempts.get(challenge.pk)) for challenge in open_challenges]


@router.post("/challenges/{int:challenge_id}/start", response={201: SessionOut}, auth=django_auth)
def start_challenge(request, challenge_id: int):
    """Démarre le défi : une seule tentative, le chrono ne s'arrête plus."""
    user = contributor(request)
    challenge = get_object_or_404(Challenge.objects.select_related("template__exercise"), pk=challenge_id)
    return 201, challenges.start(user, challenge)
