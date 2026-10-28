"""API des signalements : déposer, et suivre les siens."""

from datetime import datetime
from typing import Literal

from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle
from pydantic import Field

from accounts.permissions import contributor
from content.models import Exercise, Solution

from .models import Report
from .services import create_report

router = Router(tags=["modération"])


class ReportIn(Schema):
    target: Literal["exercise", "solution"]
    target_id: int
    reason: Literal["doublon", "plagiat", "erreur", "inapproprie", "ia_non_declaree"]
    details: str = Field(default="", max_length=1000)
    duplicate_of: int | None = Field(None, description="Pour un doublon : l'autre exercice.")


class ReportOut(Schema):
    """Un signalement vu par son auteur : le motif de la décision reste entre la
    modération et l'auteur du contenu."""

    id: int
    target: str
    exercise_id: int
    title: str
    reason: str
    reason_label: str
    status: str
    status_label: str
    created_at: datetime
    decided_at: datetime | None

    @staticmethod
    def resolve_target(obj):
        return "exercise" if obj.exercise_id else "solution"

    @staticmethod
    def resolve_exercise_id(obj):
        return obj.exercise_id or obj.solution.exercise_id

    @staticmethod
    def resolve_title(obj):
        exercise = obj.exercise or obj.solution.exercise
        return exercise.title if obj.exercise_id else f"Une solution de « {exercise.title} »"

    @staticmethod
    def resolve_reason_label(obj):
        return obj.get_reason_display()

    @staticmethod
    def resolve_status_label(obj):
        return obj.get_status_display()


@router.post(
    "/reports",
    response={201: ReportOut},
    auth=django_auth,
    throttle=[AuthRateThrottle("20/h")],
)
def report(request, payload: ReportIn):
    """Signale un exercice publié ou une solution validée. Un doublon demande le
    niveau Relecteur et l'exercice d'origine ; il rejoint la file des doublons."""
    user = contributor(request)
    exercise = solution = None
    if payload.target == "exercise":
        exercise = get_object_or_404(Exercise, pk=payload.target_id, status=Exercise.Status.PUBLISHED)
    else:
        solution = get_object_or_404(
            Solution.objects.select_related("exercise"),
            pk=payload.target_id,
            status=Solution.Status.VALIDATED,
        )
    duplicate_of = None
    if payload.duplicate_of is not None:
        duplicate_of = Exercise.objects.filter(
            pk=payload.duplicate_of, status=Exercise.Status.PUBLISHED
        ).first()
        if duplicate_of is None:
            raise HttpError(422, "Exercice d'origine introuvable : vérifie le lien ou le numéro.")
    created = create_report(
        user,
        reason=payload.reason,
        exercise=exercise,
        solution=solution,
        details=payload.details,
        duplicate_of=duplicate_of,
    )
    return 201, created


@router.get("/reports/mine", response=list[ReportOut], auth=django_auth)
def my_reports(request):
    return (
        Report.objects.filter(reporter=request.auth)
        .select_related("exercise", "solution__exercise")
        .order_by("-created_at")
    )
