"""API des signalements : déposer, et suivre les siens."""

from datetime import datetime
from typing import Literal

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth
from pydantic import Field

from accounts.permissions import contributor, is_moderator
from config.throttles import AuthRouteThrottle
from content.models import Exercise, Solution

from . import comprehension
from .models import ComprehensionQuestion, IntegritySignal, Report, Sanction
from .services import (
    APPEAL_WINDOW,
    SANCTION_TEXT,
    answer_deadline,
    answer_question,
    answer_signal,
    can_evaluate,
    create_appeal,
    create_report,
    evaluate_question,
    open_question,
)

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
    throttle=[AuthRouteThrottle("signalement", "20/h")],
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


class AnswerIn(Schema):
    answer: str = Field(min_length=3, max_length=2000)


@router.post("/integrity/{int:signal_id}/answer", response={204: None}, auth=django_auth)
def answer_integrity_question(request, signal_id: int, payload: AnswerIn):
    """Réponse de l'auteur à la question neutre sur sa solution en vérification."""
    answer_signal(get_object_or_404(IntegritySignal, pk=signal_id, user=request.auth), request.auth, payload.answer)
    return 204, None


# ---------------------------------------------------------------- mes décisions, appels


class DecisionOut(Schema):
    """Une décision qui me concerne : sanction, retrait d'un contenu, plagiat confirmé."""

    type: Literal["sanction", "report", "signal"]
    id: int
    title: str
    reason: str
    decided_at: datetime | None
    ends_at: datetime | None = None
    appeal_deadline: datetime | None
    can_appeal: bool
    appeal_status: str | None
    appeal_status_label: str | None
    appeal_note: str | None


class AppealIn(Schema):
    type: Literal["sanction", "report", "signal"]
    id: int
    statement: str = Field(min_length=10, max_length=3000)


def _decision_out(kind, decision, title, reason, decided_at, ends_at=None):
    appeal = getattr(decision, "appeal", None)
    deadline = decided_at + APPEAL_WINDOW if decided_at else None
    return {
        "type": kind,
        "id": decision.pk,
        "title": title,
        "reason": reason,
        "decided_at": decided_at,
        "ends_at": ends_at,
        "appeal_deadline": deadline,
        "can_appeal": appeal is None and deadline is not None and timezone.now() <= deadline,
        "appeal_status": appeal.status if appeal else None,
        "appeal_status_label": appeal.get_status_display() if appeal else None,
        "appeal_note": appeal.decision_note if appeal and appeal.decision_note else None,
    }


@router.get("/decisions/mine", response=list[DecisionOut], auth=django_auth)
def my_decisions(request):
    """Ce que la modération a décidé à mon sujet, avec le motif et l'appel possible."""
    user = request.auth
    items = []
    for decision in Sanction.objects.filter(user=user).select_related("appeal"):
        items.append(
            _decision_out(
                "sanction", decision, SANCTION_TEXT[decision.kind], decision.reason, decision.created_at, decision.ends_at
            )
        )
    removals = (
        Report.objects.filter(status=Report.Status.CONFIRMED)
        .filter(Q(exercise__author=user) | Q(solution__author=user))
        .exclude(reason__in=[Report.Reason.ERROR, Report.Reason.DUPLICATE])
        .select_related("exercise", "solution__exercise")
    )
    seen = set()
    for report in removals:
        # Plusieurs signalements pour un même contenu : une seule décision.
        key = (report.exercise_id, report.solution_id, report.reason)
        if key in seen:
            continue
        seen.add(key)
        what = report.exercise.title if report.exercise_id else f"Ta solution de « {report.solution.exercise.title} »"
        items.append(
            _decision_out("report", report, f"{report.get_reason_display()} : {what}", report.decision_note, report.decided_at)
        )
    for signal in IntegritySignal.objects.filter(user=user, status=IntegritySignal.Status.CONFIRMED).select_related(
        "solution__exercise"
    ):
        title = f"Plagiat confirmé : ta solution de « {signal.solution.exercise.title} »" if signal.solution else "Plagiat confirmé"
        items.append(_decision_out("signal", signal, title, signal.decision_note, signal.decided_at))
    return sorted(items, key=lambda item: item["decided_at"] or timezone.now(), reverse=True)


@router.post("/appeals", response={201: None}, auth=django_auth)
def appeal(request, payload: AppealIn):
    """Faire appel, sous 14 jours ; un autre modérateur répond sous 7 jours."""
    model = {"sanction": Sanction, "report": Report, "signal": IntegritySignal}[payload.type]
    create_appeal(request.auth, get_object_or_404(model, pk=payload.id), payload.statement)
    return 201, None


# ---------------------------------------------------------------- questions de compréhension

Question = ComprehensionQuestion.Status


class QuestionOut(Schema):
    """Question posée au membre. L'énoncé, la solution et la question ne sont envoyés
    qu'une fois la question ouverte : les 5 minutes partent de là."""

    id: int
    exercise_id: int
    exercise_title: str
    status: str
    status_label: str
    open_until: datetime | None
    answer_until: datetime | None
    statement: str | None
    solution_body: str | None
    question: str | None
    answer: str
    evaluation_note: str


def _question_out(question):
    shown = question.status not in (Question.TO_WRITE, Question.SENT)
    solution = question.solution
    return {
        "id": question.pk,
        "exercise_id": solution.exercise_id,
        "exercise_title": solution.exercise.title,
        "status": question.status,
        "status_label": question.get_status_display(),
        "open_until": question.sent_at + comprehension.OPEN_WITHIN if question.sent_at else None,
        "answer_until": answer_deadline(question),
        "statement": (solution.variant_statement or solution.exercise.statement) if shown else None,
        "solution_body": solution.body if shown else None,
        "question": question.question if shown else None,
        "answer": question.answer,
        "evaluation_note": question.evaluation_note,
    }


def _my_question(request, question_id):
    return get_object_or_404(
        ComprehensionQuestion.objects.select_related("solution__exercise"), pk=question_id, user=request.auth
    )


@router.get("/questions/mine", response=list[QuestionOut], auth=django_auth)
def my_questions(request):
    """Questions envoyées : à ouvrir sous 72 h, puis 5 minutes pour répondre."""
    questions = (
        ComprehensionQuestion.objects.filter(user=request.auth)
        .exclude(status__in=[Question.TO_WRITE, Question.DROPPED])
        .select_related("solution__exercise")
    )
    return [_question_out(question) for question in questions]


@router.post("/questions/{int:question_id}/open", response=QuestionOut, auth=django_auth)
def open_my_question(request, question_id: int):
    return _question_out(open_question(_my_question(request, question_id), request.auth))


class AnswerIn(Schema):
    answer: str = Field(min_length=1, max_length=3000)


@router.post("/questions/{int:question_id}/answer", response=QuestionOut, auth=django_auth)
def answer_my_question(request, question_id: int, payload: AnswerIn):
    return _question_out(answer_question(_my_question(request, question_id), request.auth, payload.answer))


class QuestionToEvaluateOut(Schema):
    """Réponse à évaluer, sans le nom de l'auteur."""

    id: int
    exercise_title: str
    statement: str
    solution_body: str
    question: str
    expected_points: list[str]
    answer: str
    answered_at: datetime
    llm_assessment: str | None
    llm_assessment_label: str | None
    llm_rationale: str


@router.get("/questions/to-evaluate", response=list[QuestionToEvaluateOut], auth=django_auth)
def questions_to_evaluate(request):
    """Réponses à évaluer, ouvertes aux relecteurs de niveau 3 et aux modérateurs."""
    user = request.auth
    if user.trust_level < user.TrustLevel.EXPERT and not is_moderator(user):
        raise HttpError(403, "Les questions de compréhension sont évaluées par les experts et les modérateurs.")
    answered = ComprehensionQuestion.objects.filter(status=Question.ANSWERED).select_related("solution__exercise")
    return [
        {
            "id": question.pk,
            "exercise_title": question.solution.exercise.title,
            "statement": question.solution.variant_statement or question.solution.exercise.statement,
            "solution_body": question.solution.body,
            "question": question.question,
            "expected_points": question.expected_points,
            "answer": question.answer,
            "answered_at": question.answered_at,
            "llm_assessment": question.llm_assessment or None,
            "llm_assessment_label": question.get_llm_assessment_display() if question.llm_assessment else None,
            "llm_rationale": question.llm_rationale,
        }
        for question in answered
        if can_evaluate(user, question)
    ]


class EvaluationIn(Schema):
    passed: bool
    note: str = Field(default="", max_length=1000)


@router.post("/questions/{int:question_id}/evaluate", response={204: None}, auth=django_auth)
def evaluate(request, question_id: int, payload: EvaluationIn):
    question = get_object_or_404(ComprehensionQuestion.objects.select_related("solution__exercise"), pk=question_id)
    evaluate_question(question, passed=payload.passed, evaluator=request.auth, note=payload.note)
    return 204, None
