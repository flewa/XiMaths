"""Espace de modération de l'équipe : les files à traiter (signalements, messages signalés,
appels), la fiche de chaque membre et le journal des décisions.

Tout y passe par les mêmes services que l'admin : chaque décision est humaine, motivée,
notifiée à la personne concernée, contestable en appel, et inscrite au journal. Un
modérateur ne tranche jamais ce qui le concerne : ses propres contenus, ses propres
décisions en appel, son propre compte.
"""

from datetime import datetime
from typing import Literal

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Field, Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth

from accounts.permissions import is_moderator
from config.errors import RuleError
from content import photos
from content.api import PhotoOut
from content.models import Exercise, Message, Review, Solution
from gamification.services import balance

from .models import Appeal, IntegritySignal, ModerationLog, Report, Sanction
from .services import (
    APPEAL_RESPONSE,
    SANCTION_TEXT,
    active_sanctions,
    decide_appeal,
    flagged_messages,
    keep_message,
    lift,
    open_report_groups,
    pending_counts,
    remove_message,
    resolve_report,
    sanction,
    set_moderator,
    target_label,
)

User = get_user_model()
router = Router(tags=["équipe de modération"])
Reason = Report.Reason

SanctionKind = Literal["avertissement", "exclusion_classements", "suspension", "bannissement"]

# Ce que change un signalement confirmé, pour que la personne qui tranche le sache avant.
EFFECTS = {
    ("exercise", Reason.PLAGIARISM): "Si tu confirmes, l'exercice est retiré et ses points annulés.",
    ("exercise", Reason.INAPPROPRIATE): "Si tu confirmes, l'exercice est retiré et ses points annulés.",
    ("exercise", Reason.ERROR): "Si tu confirmes, rien n'est retiré : l'énoncé se corrige à part, puis on confirme.",
    ("solution", Reason.PLAGIARISM): "Si tu confirmes, la copie est masquée, ses points annulés, et 50 points retirés.",
    ("solution", Reason.INAPPROPRIATE): "Si tu confirmes, la copie est masquée et ses points annulés.",
    ("solution", Reason.UNDECLARED_AI): "Si tu confirmes, les points de la copie sont annulés, sans étiquette publique.",
    ("solution", Reason.ERROR): "Si tu confirmes, rien n'est retiré : l'erreur se juge dans les relectures.",
}


def team(request):
    """L'équipe : modérateurs nommés et administrateurs, avec un compte actif."""
    user = request.auth
    if not is_moderator(user) or user.status != User.Status.ACTIVE:
        raise HttpError(403, "Réservé à l'équipe de modération.")
    return user


def refused(error):
    return HttpError(409, str(error))


# ---------------------------------------------------------------- schémas communs


class MemberBriefOut(Schema):
    """Un membre dans une file : de quoi juger s'il récidive."""

    username: str
    status: str
    status_label: str
    active_sanction: str | None
    # Sanctions et retraits de contenu passés.
    past_decisions: int


def brief(user):
    if user is None:
        return None
    current = active_sanctions(user).order_by("-created_at").first()
    removals = (
        Report.objects.filter(status=Report.Status.CONFIRMED)
        .filter(Q(exercise__author=user) | Q(solution__author=user))
        .exclude(reason__in=[Reason.ERROR, Reason.DUPLICATE])
        .values("exercise_id", "solution_id", "reason")
        .distinct()
        .count()
    )
    return {
        "username": user.username,
        "status": user.status,
        "status_label": user.get_status_display(),
        "active_sanction": SANCTION_TEXT[current.kind] if current else None,
        "past_decisions": Sanction.objects.filter(user=user).count()
        + removals
        + Message.objects.filter(author=user, removed_by_team=True).count(),
    }


class SummaryOut(Schema):
    reports: int
    messages: int
    appeals: int
    appeals_overdue: int
    duplicates: int


@router.get("/moderation/summary", response=SummaryOut, auth=django_auth)
def summary(request):
    team(request)
    counts = pending_counts()
    late = timezone.now() - APPEAL_RESPONSE
    counts["appeals_overdue"] = Appeal.objects.filter(status=Appeal.Status.PENDING, created_at__lt=late).count()
    return counts


# ---------------------------------------------------------------- signalements


class ReporterOut(Schema):
    username: str
    details: str
    created_at: datetime


class ReportGroupOut(Schema):
    id: int
    reason: str
    reason_label: str
    target: Literal["exercise", "solution"]
    exercise_id: int
    exercise_title: str
    # L'énoncé (pour une copie : celui que son auteur a reçu) et, pour une copie, ses photos.
    statement: str
    photos: list[PhotoOut]
    solution_status: str | None
    author: MemberBriefOut | None
    reports: list[ReporterOut]
    created_at: datetime
    effect: str
    # Faux si le contenu est celui du modérateur : un autre doit trancher.
    can_decide: bool


class ReportDecisionIn(Schema):
    confirmed: bool
    note: str = Field(default="", max_length=2000)
    # Sanction à prononcer en plus contre l'auteur du contenu, avec le même motif.
    sanction: SanctionKind | None = None


def group_out(report, me):
    target = "exercise" if report.exercise_id else "solution"
    solution = report.solution
    exercise = report.exercise or solution.exercise
    content = report.exercise or solution
    same = (
        Report.objects.filter(
            status=Report.Status.OPEN, reason=report.reason, exercise=report.exercise, solution=report.solution
        )
        .select_related("reporter")
        .order_by("created_at")
    )
    return {
        "id": report.pk,
        "reason": report.reason,
        "reason_label": report.get_reason_display(),
        "target": target,
        "exercise_id": exercise.pk,
        "exercise_title": exercise.title,
        "statement": (solution.variant_statement or exercise.statement) if solution else exercise.statement,
        "photos": photos.described(solution) if solution else [],
        "solution_status": solution.get_status_display() if solution else None,
        "author": brief(content.author),
        "reports": [
            {"username": each.reporter.username, "details": each.details, "created_at": each.created_at} for each in same
        ],
        "created_at": report.created_at,
        "effect": EFFECTS.get((target, report.reason), ""),
        "can_decide": content.author_id != me.pk,
    }


@router.get("/moderation/reports", response=list[ReportGroupOut], auth=django_auth)
def reports_queue(request):
    """Signalements à trancher, les plus anciens d'abord. Les doublons ont leur propre file."""
    me = team(request)
    return [group_out(report, me) for report in open_report_groups()]


@router.post("/moderation/reports/{int:report_id}/decide", response={204: None}, auth=django_auth)
def decide_report(request, report_id: int, payload: ReportDecisionIn):
    me = team(request)
    report = get_object_or_404(
        Report.objects.select_related("exercise", "solution__exercise"), pk=report_id, status=Report.Status.OPEN
    )
    content = report.exercise or report.solution
    if content.author_id == me.pk:
        raise HttpError(403, "Ce signalement vise ton propre contenu : un autre membre de l'équipe le tranche.")
    if payload.sanction and not payload.confirmed:
        raise HttpError(422, "Une sanction suit un signalement confirmé.")
    try:
        resolve_report(report, confirmed=payload.confirmed, moderator=me, note=payload.note)
        if payload.sanction and content.author is not None:
            sanction(
                content.author,
                payload.sanction,
                reason=f"{report.get_reason_display()} sur {target_label(report)}. {payload.note.strip()}",
                moderator=me,
                report=report,
            )
    except RuleError as error:
        raise refused(error)
    return 204, None


# ---------------------------------------------------------------- messages signalés


class FlagOut(Schema):
    username: str
    created_at: datetime


class FlaggedMessageOut(Schema):
    id: int
    body: str
    created_at: datetime
    exercise_id: int
    exercise_title: str
    author: MemberBriefOut | None
    # Pour une réponse : le début de la question à laquelle elle répond.
    in_reply_to: str | None
    flags: list[FlagOut]
    # Déjà examiné et gardé une fois, puis signalé à nouveau.
    kept_before: bool
    can_decide: bool


class MessageDecisionIn(Schema):
    remove: bool
    reason: str = Field(default="", max_length=1000)


@router.get("/moderation/messages", response=list[FlaggedMessageOut], auth=django_auth)
def messages_queue(request):
    me = team(request)
    out = []
    queue = flagged_messages().select_related("exercise", "author", "parent").order_by("created_at")
    for message in queue:
        flags = message.flags.select_related("user").order_by("created_at")
        if message.flags_reviewed_at:
            flags = flags.filter(created_at__gt=message.flags_reviewed_at)
        out.append(
            {
                "id": message.pk,
                "body": message.body,
                "created_at": message.created_at,
                "exercise_id": message.exercise_id,
                "exercise_title": message.exercise.title,
                "author": brief(message.author),
                "in_reply_to": message.parent.body[:200] if message.parent else None,
                "flags": [{"username": flag.user.username, "created_at": flag.created_at} for flag in flags],
                "kept_before": message.flags_reviewed_at is not None,
                "can_decide": message.author_id != me.pk,
            }
        )
    return out


@router.post("/moderation/messages/{int:message_id}/decide", response={204: None}, auth=django_auth)
def decide_message(request, message_id: int, payload: MessageDecisionIn):
    me = team(request)
    message = get_object_or_404(Message.objects.select_related("exercise", "author"), pk=message_id, removed_at=None)
    if message.author_id == me.pk:
        raise HttpError(403, "C'est ton message : un autre membre de l'équipe l'examine.")
    try:
        if payload.remove:
            remove_message(message, moderator=me, reason=payload.reason)
        else:
            keep_message(message, moderator=me)
    except RuleError as error:
        raise refused(error)
    return 204, None


# ---------------------------------------------------------------- appels


class AppealQueueOut(Schema):
    id: int
    member: MemberBriefOut
    statement: str
    created_at: datetime
    due_at: datetime
    overdue: bool
    decision_type: Literal["sanction", "report", "signal", "message"]
    decision_title: str
    decision_reason: str
    decided_at: datetime | None
    decided_by: str | None
    # Le contenu concerné, quand il y en a un.
    url: str | None
    # Faux pour l'auteur de la décision : un autre modérateur tranche l'appel.
    can_decide: bool


class AppealDecisionIn(Schema):
    overturn: bool
    note: str = Field(min_length=1, max_length=2000)


def appeal_out(appeal, me):
    decision = appeal.decision
    if isinstance(decision, Sanction):
        kind, title, reason = "sanction", SANCTION_TEXT[decision.kind], decision.reason
        decided_at, decider, url = decision.created_at, decision.decided_by, None
    elif isinstance(decision, Report):
        kind = "report"
        title = f"{decision.get_reason_display()} sur {target_label(decision)}"
        reason, decided_at, decider = decision.decision_note, decision.decided_at, decision.decided_by
        url = f"/exercices/{decision.exercise_id or decision.solution.exercise_id}"
    elif isinstance(decision, Message):
        kind, title = "message", f"Message retiré sous « {decision.exercise.title} »"
        reason, decided_at, decider = decision.removal_reason, decision.removed_at, decision.removed_by
        url = f"/exercices/{decision.exercise_id}#discussion"
    else:
        kind, title = "signal", "Plagiat confirmé"
        reason, decided_at, decider, url = decision.decision_note, decision.decided_at, decision.decided_by, None
    due = appeal.created_at + APPEAL_RESPONSE
    return {
        "id": appeal.pk,
        "member": brief(appeal.user),
        "statement": appeal.statement,
        "created_at": appeal.created_at,
        "due_at": due,
        "overdue": timezone.now() > due,
        "decision_type": kind,
        "decision_title": title,
        "decision_reason": reason,
        "decided_at": decided_at,
        "decided_by": decider.username if decider else None,
        "url": url,
        "can_decide": decider is None or decider.pk != me.pk,
    }


@router.get("/moderation/appeals", response=list[AppealQueueOut], auth=django_auth)
def appeals_queue(request):
    me = team(request)
    appeals = Appeal.objects.filter(status=Appeal.Status.PENDING).select_related(
        "user",
        "sanction__decided_by",
        "report__decided_by",
        "report__exercise",
        "report__solution__exercise",
        "signal__decided_by",
        "message__exercise",
        "message__removed_by",
    )
    return [appeal_out(appeal, me) for appeal in appeals.order_by("created_at")]


@router.post("/moderation/appeals/{int:appeal_id}/decide", response={204: None}, auth=django_auth)
def decide(request, appeal_id: int, payload: AppealDecisionIn):
    me = team(request)
    appeal = get_object_or_404(Appeal, pk=appeal_id)
    if appeal.user_id == me.pk:
        raise HttpError(403, "C'est ton propre appel : un autre membre de l'équipe le tranche.")
    try:
        decide_appeal(appeal, overturn=payload.overturn, moderator=me, note=payload.note)
    except RuleError as error:
        raise refused(error)
    return 204, None


# ---------------------------------------------------------------- fiche d'un membre


class SanctionOut(Schema):
    id: int
    kind: str
    label: str
    reason: str
    created_at: datetime
    ends_at: datetime | None
    active: bool
    decided_by: str | None
    lifted_reason: str
    appeal: str | None


class RemovalOut(Schema):
    what: str
    reason: str
    decided_at: datetime | None
    decided_by: str | None
    url: str | None
    appeal: str | None


class MemberMessageOut(Schema):
    id: int
    body: str
    created_at: datetime
    exercise_id: int
    exercise_title: str
    removed: bool


class LogOut(Schema):
    id: int
    created_at: datetime
    actor: str | None
    action: str
    action_label: str
    summary: str
    member: str | None
    url: str


class MemberFileOut(Schema):
    username: str
    joined_at: datetime
    status: str
    status_label: str
    trust_level: int
    trust_label: str
    is_staff: bool
    is_moderator: bool
    email_verified: bool
    points: int
    exercises: int
    solutions: int
    reviews: int
    messages: int
    reports_made: int
    reports_confirmed: int
    reports_rejected: int
    sanctions: list[SanctionOut]
    removals: list[RemovalOut]
    recent_messages: list[MemberMessageOut]
    log: list[LogOut]
    # Ce que la personne qui consulte peut faire.
    can_sanction: bool
    can_appoint: bool


def log_out(entry):
    return {
        "id": entry.pk,
        "created_at": entry.created_at,
        "actor": entry.actor.username if entry.actor else None,
        "action": entry.action,
        "action_label": entry.get_action_display(),
        "summary": entry.summary,
        "member": entry.member.username if entry.member else None,
        "url": entry.url,
    }


def appeal_label(decision):
    appeal = getattr(decision, "appeal", None)
    return f"Appel : {appeal.get_status_display().lower()}" if appeal else None


def member_file(member, me):
    now = timezone.now()
    sanctions = [
        {
            "id": each.pk,
            "kind": each.kind,
            "label": SANCTION_TEXT[each.kind],
            "reason": each.reason,
            "created_at": each.created_at,
            "ends_at": each.ends_at,
            "active": each.lifted_at is None
            and each.kind != Sanction.Kind.WARNING
            and (each.ends_at is None or each.ends_at > now),
            "decided_by": each.decided_by.username if each.decided_by else None,
            "lifted_reason": each.lifted_reason,
            "appeal": appeal_label(each),
        }
        for each in Sanction.objects.filter(user=member).select_related("decided_by", "appeal")
    ]
    removals = []
    seen = set()
    confirmed = (
        Report.objects.filter(status=Report.Status.CONFIRMED)
        .filter(Q(exercise__author=member) | Q(solution__author=member))
        .exclude(reason__in=[Reason.ERROR, Reason.DUPLICATE])
        .select_related("exercise", "solution__exercise", "decided_by")
        .order_by("-decided_at")
    )
    for report in confirmed:
        key = (report.exercise_id, report.solution_id, report.reason)
        if key in seen:
            continue
        seen.add(key)
        removals.append(
            {
                "what": f"{report.get_reason_display()} sur {target_label(report)}",
                "reason": report.decision_note,
                "decided_at": report.decided_at,
                "decided_by": report.decided_by.username if report.decided_by else None,
                "url": f"/exercices/{report.exercise_id or report.solution.exercise_id}",
                "appeal": appeal_label(report),
            }
        )
    for message in Message.objects.filter(author=member, removed_by_team=True).select_related("exercise", "removed_by"):
        removals.append(
            {
                "what": f"Message sous « {message.exercise.title} »",
                "reason": message.removal_reason,
                "decided_at": message.removed_at,
                "decided_by": message.removed_by.username if message.removed_by else None,
                "url": f"/exercices/{message.exercise_id}#discussion",
                "appeal": appeal_label(message),
            }
        )
    for signal in IntegritySignal.objects.filter(user=member, status=IntegritySignal.Status.CONFIRMED):
        removals.append(
            {
                "what": "Plagiat confirmé",
                "reason": signal.decision_note,
                "decided_at": signal.decided_at,
                "decided_by": None,
                "url": None,
                "appeal": appeal_label(signal),
            }
        )
    removals.sort(key=lambda item: item["decided_at"] or now, reverse=True)
    made = Report.objects.filter(reporter=member).values("status").annotate(count=Count("pk"))
    made = {row["status"]: row["count"] for row in made}
    return {
        "username": member.username,
        "joined_at": member.date_joined,
        "status": member.status,
        "status_label": member.get_status_display(),
        "trust_level": member.trust_level,
        "trust_label": member.get_trust_level_display(),
        "is_staff": member.is_staff,
        "is_moderator": is_moderator(member),
        "email_verified": member.email_verified_at is not None,
        "points": balance(member),
        "exercises": Exercise.objects.filter(author=member).exclude(status=Exercise.Status.DRAFT).count(),
        "solutions": Solution.objects.filter(author=member).exclude(status=Solution.Status.DRAFT).count(),
        "reviews": Review.objects.filter(reviewer=member).exclude(submitted_at=None).count(),
        "messages": Message.objects.filter(author=member).count(),
        "reports_made": sum(made.values()),
        "reports_confirmed": made.get(Report.Status.CONFIRMED, 0),
        "reports_rejected": made.get(Report.Status.REJECTED, 0),
        "sanctions": sanctions,
        "removals": removals,
        "recent_messages": [
            {
                "id": message.pk,
                "body": message.body,
                "created_at": message.created_at,
                "exercise_id": message.exercise_id,
                "exercise_title": message.exercise.title,
                "removed": message.removed_at is not None,
            }
            for message in Message.objects.filter(author=member).select_related("exercise").order_by("-created_at")[:10]
        ],
        "log": [log_out(entry) for entry in ModerationLog.objects.filter(member=member).select_related("actor")[:30]],
        # On ne se sanctionne pas soi-même, et seul un administrateur sanctionne un modérateur.
        "can_sanction": member.pk != me.pk and not member.is_staff and (me.is_staff or not is_moderator(member)),
        "can_appoint": me.is_staff and not member.is_staff and member.pk != me.pk,
    }


class SanctionIn(Schema):
    kind: SanctionKind
    reason: str = Field(min_length=1, max_length=2000)


class LiftIn(Schema):
    reason: str = Field(min_length=1, max_length=200)


class ModeratorIn(Schema):
    moderator: bool


def get_member(username):
    return get_object_or_404(User, username=username, is_active=True)


@router.get("/moderation/members/{username}", response=MemberFileOut, auth=django_auth)
def get_member_file(request, username: str):
    me = team(request)
    return member_file(get_member(username), me)


@router.post("/moderation/members/{username}/sanctions", response=MemberFileOut, auth=django_auth)
def add_sanction(request, username: str, payload: SanctionIn):
    me = team(request)
    member = get_member(username)
    if not member_file(member, me)["can_sanction"]:
        raise HttpError(403, "Tu ne peux pas sanctionner ce compte.")
    try:
        sanction(member, payload.kind, reason=payload.reason, moderator=me)
    except RuleError as error:
        raise refused(error)
    return member_file(member, me)


@router.post("/moderation/sanctions/{int:sanction_id}/lift", response=MemberFileOut, auth=django_auth)
def lift_sanction(request, sanction_id: int, payload: LiftIn):
    me = team(request)
    decision = get_object_or_404(Sanction.objects.select_related("user"), pk=sanction_id, lifted_at=None)
    if decision.user_id == me.pk:
        raise HttpError(403, "Une sanction qui te vise est levée par un autre membre de l'équipe.")
    lift(decision, reason=payload.reason.strip(), moderator=me)
    return member_file(decision.user, me)


@router.post("/moderation/members/{username}/moderator", response=MemberFileOut, auth=django_auth)
def appoint(request, username: str, payload: ModeratorIn):
    me = team(request)
    member = get_member(username)
    # Réservé aux administrateurs : set_moderator lève PermissionDenied (403) sinon.
    try:
        set_moderator(member, payload.moderator, by=me)
    except RuleError as error:
        raise refused(error)
    return member_file(member, me)


# ---------------------------------------------------------------- journal


@router.get("/moderation/log", response=list[LogOut], auth=django_auth)
def journal(request, before: int | None = None):
    """Les 100 dernières décisions de l'équipe ; `before` pour remonter plus loin."""
    team(request)
    entries = ModerationLog.objects.select_related("actor", "member")
    if before is not None:
        entries = entries.filter(pk__lt=before)
    return [log_out(entry) for entry in entries[:100]]

