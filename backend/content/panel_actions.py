"""Actions du panneau d'administration : ce qu'un administrateur peut décider lui-même.

Chaque action demande un motif, prévient la personne concernée quand elle la touche, et
s'inscrit au journal de modération. Les retraits de contenu passent par un signalement que
l'administrateur dépose et tranche aussitôt : son auteur reçoit le motif et peut faire appel,
comme pour tout retrait, et un autre membre de l'équipe examine l'appel.

Un administrateur ne décide jamais de ce qui le concerne : sa propre copie, son propre
exercice, son propre compte.
"""

from datetime import datetime
from typing import Literal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Field, Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth

from accounts.services import delete_account
from config.errors import RuleError
from gamification.models import PointTransaction
from gamification.services import award, restore_points_from, reverse_points_from
from moderation.models import ModerationLog, Report
from moderation.services import create_report, log_action, resolve_report
from notifications.models import Notification
from notifications.services import notify

from .api import ExerciseIn, draft_fields
from .models import Exercise, Review, Solution
from .panel import admin
from .services import _close_as_needs_work, _validate, assign_reviewers

User = get_user_model()
router = Router(tags=["administration"])
Action = ModerationLog.Action
Kind = Notification.Kind
Status = Solution.Status
TL = User.TrustLevel

REMOVALS = {"remove_plagiarism": Report.Reason.PLAGIARISM, "remove_inappropriate": Report.Reason.INAPPROPRIATE}
MAX_ADJUSTMENT = 1000


def refused(error):
    return HttpError(409, str(error))


def reason_of(text):
    text = text.strip()
    if not text:
        raise HttpError(422, "Indique le motif : il est gardé au journal, et envoyé à la personne concernée.")
    return text


def remove_by_report(me, kind, note, *, exercise=None, solution=None):
    """Retrait par l'administration : un signalement déposé et confirmé aussitôt, pour que
    l'auteur reçoive le motif et puisse faire appel depuis Mes décisions."""
    report = create_report(me, reason=REMOVALS[kind], exercise=exercise, solution=solution, details=note)
    return resolve_report(report, confirmed=True, moderator=me, note=note)


# ---------------------------------------------------------------- copies


class SolutionDecisionIn(Schema):
    decision: Literal["validate", "needs_work", "review_again", "remove_plagiarism", "remove_inappropriate"]
    reason: str = Field(max_length=2000)


ALLOWED = {
    "validate": {Status.UNDER_REVIEW, Status.NEEDS_WORK},
    "needs_work": {Status.UNDER_REVIEW, Status.VALIDATED},
    "review_again": {Status.NEEDS_WORK, Status.VALIDATED},
    "remove_plagiarism": {Status.UNDER_REVIEW, Status.VALIDATED, Status.NEEDS_WORK},
    "remove_inappropriate": {Status.UNDER_REVIEW, Status.VALIDATED, Status.NEEDS_WORK},
}
SUMMARIES = {
    "validate": "Copie validée",
    "needs_work": "Copie renvoyée à reprendre",
    "review_again": "Copie remise en relecture",
}


@transaction.atomic
def decide_solution(solution, decision, *, me, reason, now=None):
    if solution.author_id == me.pk:
        raise PermissionDenied("C'est ta copie : un autre membre de l'équipe en décide.")
    if solution.status not in ALLOWED[decision]:
        raise RuleError(f"Impossible depuis le statut « {solution.get_status_display()} ».")
    now = now or timezone.now()
    url = f"/exercices/{solution.exercise_id}"
    if decision in REMOVALS:
        remove_by_report(me, decision, reason, solution=solution)
        return solution
    if decision == "validate":
        _validate(solution, now=now)
    elif decision == "needs_work":
        if solution.status == Status.UNDER_REVIEW:
            _close_as_needs_work(solution, agreeing={Review.Verdict.INCORRECT}, now=now)
        else:
            reverse_points_from(solution, now=now)
            solution.status = Status.NEEDS_WORK
            solution.validated_at = None
            solution.model_at = None
            solution.save(update_fields=["status", "validated_at", "model_at", "updated_at"])
        notify(
            solution.author,
            Kind.SOLUTION_NEEDS_WORK,
            "L'équipe a renvoyé ta copie à reprendre",
            f"Motif : {reason}",
            url,
            now=now,
        )
    else:
        if solution.status == Status.VALIDATED:
            reverse_points_from(solution, now=now)
        solution.status = Status.UNDER_REVIEW
        solution.validated_at = None
        solution.model_at = None
        solution.review_round += 1
        solution.save(update_fields=["status", "validated_at", "model_at", "review_round", "updated_at"])
        assign_reviewers(solution, now=now)
        notify(
            solution.author,
            Kind.SOLUTION_REVIEWED,
            "Ta copie repart en relecture",
            f"L'équipe la fait relire à nouveau. Motif : {reason}",
            url,
            now=now,
        )
    log_action(
        me,
        Action.SOLUTION_DECIDED,
        f"{SUMMARIES[decision]} sur « {solution.exercise.title} ». Motif : {reason}",
        member=solution.author,
        url=url,
    )
    return solution


@router.post("/panel/solutions/{int:solution_id}/decide", response={204: None}, auth=django_auth)
def solution_decision(request, solution_id: int, payload: SolutionDecisionIn):
    me = admin(request)
    solution = get_object_or_404(Solution.objects.select_related("exercise", "author"), pk=solution_id)
    try:
        decide_solution(solution, payload.decision, me=me, reason=reason_of(payload.reason))
    except RuleError as error:
        raise refused(error)
    return 204, None


# ---------------------------------------------------------------- exercices


class PanelExerciseDetailOut(Schema):
    id: int
    title: str
    statement: str
    hints: list[str]
    final_answer: str
    difficulty: int
    primary_level: str
    levels: list[str]
    topics: list[str]
    source_type: str
    source_reference: str
    status: str
    status_label: str
    author: str | None
    published_at: datetime | None
    edited_by_team_at: datetime | None
    # Exercice de la rédaction : l'import ne touchera plus son titre ni ses chapitres une fois
    # modifié ici.
    editorial: bool


class ExerciseEditIn(ExerciseIn):
    reason: str = Field(max_length=2000)


class ExerciseStatusIn(Schema):
    action: Literal["remove_plagiarism", "remove_inappropriate", "restore"]
    reason: str = Field(max_length=2000)


def exercise_detail(exercise):
    from accounts.profile import EDITORIAL_USERNAME

    return {
        "id": exercise.pk,
        "title": exercise.title,
        "statement": exercise.statement,
        "hints": exercise.hints,
        "final_answer": exercise.final_answer,
        "difficulty": exercise.difficulty_declared,
        "primary_level": exercise.primary_level.code,
        "levels": list(exercise.levels.values_list("code", flat=True)),
        "topics": list(exercise.topics.values_list("slug", flat=True)),
        "source_type": exercise.source_type,
        "source_reference": exercise.source_reference,
        "status": exercise.status,
        "status_label": exercise.get_status_display(),
        "author": exercise.author.username if exercise.author else None,
        "published_at": exercise.published_at,
        "edited_by_team_at": exercise.edited_by_team_at,
        "editorial": bool(exercise.author and exercise.author.username == EDITORIAL_USERNAME),
    }


def get_exercise(exercise_id):
    return get_object_or_404(Exercise.objects.select_related("author", "primary_level"), pk=exercise_id)


@router.get("/panel/exercises/{int:exercise_id}", response=PanelExerciseDetailOut, auth=django_auth)
def exercise_for_edit(request, exercise_id: int):
    admin(request)
    return exercise_detail(get_exercise(exercise_id))


@router.put("/panel/exercises/{int:exercise_id}", response=PanelExerciseDetailOut, auth=django_auth)
def edit_exercise(request, exercise_id: int, payload: ExerciseEditIn):
    """Corrige un exercice, publié ou non : énoncé, indications, réponse, niveaux, chapitres."""
    me = admin(request)
    reason = reason_of(payload.reason)
    exercise = get_exercise(exercise_id)
    fields, levels, topics = draft_fields(payload)
    now = timezone.now()
    with transaction.atomic():
        for name, value in fields.items():
            setattr(exercise, name, value)
        exercise.edited_by_team_at = now
        exercise.save()
        exercise.levels.set(levels)
        exercise.topics.set(topics)
        url = f"/exercices/{exercise.pk}"
        log_action(me, Action.EXERCISE_EDITED, f"« {exercise.title} » modifié. Motif : {reason}", member=exercise.author, url=url)
        if exercise.author_id and exercise.author_id != me.pk:
            notify(exercise.author, Kind.CONTENT_REMOVED, f"L'équipe a modifié ton exercice « {exercise.title} »", f"Motif : {reason}", url, email=False, now=now)
    return exercise_detail(get_exercise(exercise_id))


@transaction.atomic
def set_exercise_status(exercise, action, *, me, reason):
    """Retire un exercice publié (son auteur reçoit le motif et peut faire appel), ou rétablit
    un exercice retiré, avec ses points."""
    if action == "restore":
        if exercise.status != Exercise.Status.REMOVED:
            raise RuleError("Seul un exercice retiré se rétablit.")
        restore_points_from(exercise)
        exercise.status = Exercise.Status.PUBLISHED
        exercise.save(update_fields=["status", "updated_at"])
        url = f"/exercices/{exercise.pk}"
        log_action(me, Action.EXERCISE_RESTORED, f"« {exercise.title} » rétabli. Motif : {reason}", member=exercise.author, url=url)
        notify(exercise.author, Kind.APPEAL_DECIDED, f"Ton exercice « {exercise.title} » est rétabli", f"Motif : {reason}", url)
    else:
        if exercise.status != Exercise.Status.PUBLISHED:
            raise RuleError("Seul un exercice publié se retire.")
        remove_by_report(me, action, reason, exercise=exercise)


@router.post("/panel/exercises/{int:exercise_id}/status", response=PanelExerciseDetailOut, auth=django_auth)
def exercise_status(request, exercise_id: int, payload: ExerciseStatusIn):
    me = admin(request)
    reason = reason_of(payload.reason)
    try:
        set_exercise_status(get_exercise(exercise_id), payload.action, me=me, reason=reason)
    except PermissionDenied as error:
        raise HttpError(403, str(error))
    except RuleError as error:
        raise refused(error)
    return exercise_detail(get_exercise(exercise_id))


# ---------------------------------------------------------------- actions groupées

# Assez pour vider une page du panneau, pas assez pour tout retirer d'un geste.
BULK_MAX = 30


class BulkFailure(Schema):
    id: int
    title: str
    error: str


class BulkOut(Schema):
    done: int
    failed: list[BulkFailure]


class BulkSolutionsIn(SolutionDecisionIn):
    ids: list[int] = Field(min_length=1, max_length=BULK_MAX)


class BulkExercisesIn(ExerciseStatusIn):
    ids: list[int] = Field(min_length=1, max_length=BULK_MAX)


def run_bulk(objects, apply, title):
    """Applique la même décision à chaque objet : chacun réussit ou échoue seul, et l'échec
    dit pourquoi (statut qui ne s'y prête pas, contenu de la personne qui décide)."""
    done, failed = 0, []
    for obj in objects:
        try:
            apply(obj)
            done += 1
        except (RuleError, PermissionDenied) as error:
            failed.append({"id": obj.pk, "title": title(obj), "error": str(error)})
    return {"done": done, "failed": failed}


@router.post("/panel/solutions/decide", response=BulkOut, auth=django_auth)
def solutions_decision(request, payload: BulkSolutionsIn):
    """Une décision, un motif, plusieurs copies : chacune est notifiée et journalisée à part."""
    me = admin(request)
    reason = reason_of(payload.reason)
    solutions = Solution.objects.filter(pk__in=payload.ids).select_related("exercise", "author").order_by("pk")
    return run_bulk(
        solutions,
        lambda solution: decide_solution(solution, payload.decision, me=me, reason=reason),
        lambda solution: solution.exercise.title,
    )


@router.post("/panel/exercises/status", response=BulkOut, auth=django_auth)
def exercises_status(request, payload: BulkExercisesIn):
    """Retirer ou rétablir plusieurs exercices d'un coup, avec un seul motif."""
    me = admin(request)
    reason = reason_of(payload.reason)
    exercises = Exercise.objects.filter(pk__in=payload.ids).select_related("author", "primary_level").order_by("pk")
    return run_bulk(
        exercises,
        lambda exercise: set_exercise_status(exercise, payload.action, me=me, reason=reason),
        lambda exercise: exercise.title,
    )


# ---------------------------------------------------------------- comptes


class PointsIn(Schema):
    amount: int = Field(ge=-MAX_ADJUSTMENT, le=MAX_ADJUSTMENT)
    reason: str = Field(max_length=2000)


class TrustIn(Schema):
    level: Literal[0, 1, 2, 3]
    reason: str = Field(max_length=2000)


class RenameIn(Schema):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[\w.-]+$")
    reason: str = Field(max_length=2000)


class DeleteIn(Schema):
    # Le pseudo, retapé : une suppression ne se fait pas par mégarde.
    confirm: str
    reason: str = Field(max_length=2000)


class AdminIn(Schema):
    admin: bool


class Done(Schema):
    username: str


def can_administer(me, member):
    """Un administrateur agit sur tout compte, sauf le sien ; sur le compte d'un autre
    administrateur, seul le propriétaire du site (superutilisateur) le peut."""
    return member.pk != me.pk and (not member.is_staff or me.is_superuser)


def member_for(me, username):
    member = get_object_or_404(User, username=username, is_active=True)
    if member.pk == me.pk:
        raise HttpError(403, "C'est ton propre compte : un autre administrateur s'en charge.")
    if not can_administer(me, member):
        raise HttpError(403, "Seul le propriétaire du site agit sur le compte d'un administrateur.")
    return member


@router.post("/panel/members/{username}/points", response=Done, auth=django_auth)
def adjust_points(request, username: str, payload: PointsIn):
    """Ajoute ou retire des points, avec un motif que le membre reçoit. Le ledger reste en
    ajout seul : c'est une écriture de plus, visible dans son historique."""
    me = admin(request)
    member = member_for(me, username)
    reason = reason_of(payload.reason)
    if payload.amount == 0:
        raise HttpError(422, "Indique un nombre de points différent de zéro.")
    with transaction.atomic():
        entry = log_action(me, Action.POINTS_ADJUSTED, f"{payload.amount:+d} points. Motif : {reason}", member=member)
        award(member, PointTransaction.Reason.ADMIN_ADJUSTMENT, entry, amount=payload.amount)
        notify(
            member,
            Kind.PROMOTION,
            f"{payload.amount:+d} points de la part de l'équipe",
            f"Motif : {reason}",
            "/progression",
            email=False,
        )
    return {"username": member.username}


@router.post("/panel/members/{username}/trust", response=Done, auth=django_auth)
def change_trust(request, username: str, payload: TrustIn):
    """Change le niveau de confiance (de Nouveau à Expert ; Modérateur se nomme à part).
    Un niveau baissé à la main peut remonter tout seul si le membre en remplit de nouveau
    les conditions."""
    me = admin(request)
    member = member_for(me, username)
    reason = reason_of(payload.reason)
    if member.trust_level >= TL.MODERATOR:
        raise HttpError(409, "Retire d'abord ce membre de l'équipe de modération.")
    if member.trust_level == payload.level:
        raise HttpError(409, "Le membre est déjà à ce niveau.")
    before, member.trust_level = member.get_trust_level_display(), payload.level
    member.save(update_fields=["trust_level"])
    after = member.get_trust_level_display()
    log_action(me, Action.TRUST_CHANGED, f"{before} → {after}. Motif : {reason}", member=member)
    notify(member, Kind.PROMOTION, f"Ton niveau est maintenant : {after}", f"Motif : {reason}", "/progression", email=False)
    return {"username": member.username}


@router.post("/panel/members/{username}/verify-email", response=Done, auth=django_auth)
def verify_email(request, username: str):
    """Vérifie l'adresse à la main, pour un membre dont l'email de confirmation n'arrive pas."""
    me = admin(request)
    member = member_for(me, username)
    if member.email_verified_at is None:
        member.email_verified_at = timezone.now()
        member.save(update_fields=["email_verified_at"])
        log_action(me, Action.EMAIL_VERIFIED, "Adresse vérifiée à la main.", member=member)
    return {"username": member.username}


@router.post("/panel/members/{username}/rename", response=Done, auth=django_auth)
def rename(request, username: str, payload: RenameIn):
    """Change un pseudo (injurieux, trompeur, données personnelles)."""
    me = admin(request)
    member = member_for(me, username)
    reason = reason_of(payload.reason)
    new = payload.username.strip()
    if User.objects.filter(username__iexact=new).exclude(pk=member.pk).exists():
        raise HttpError(409, "Ce pseudo est déjà pris.")
    old = member.username
    member.username = new
    member.save(update_fields=["username"])
    log_action(me, Action.ACCOUNT_RENAMED, f"Pseudo « {old} » changé. Motif : {reason}", member=member)
    notify(member, Kind.SANCTION, f"Ton pseudo est maintenant « {new} »", f"L'équipe l'a changé. Motif : {reason}", "/reglages", email=True)
    return {"username": member.username}


@router.post("/panel/members/{username}/delete", response=Done, auth=django_auth)
def delete_member(request, username: str, payload: DeleteIn):
    """Supprime un compte : ses données personnelles sont effacées, ses contributions restent
    publiées sans pseudo, comme quand un membre supprime lui-même son compte. Irréversible."""
    me = admin(request)
    member = member_for(me, username)
    reason = reason_of(payload.reason)
    if payload.confirm.strip() != member.username:
        raise HttpError(422, "Retape exactement le pseudo pour confirmer la suppression.")
    with transaction.atomic():
        log_action(me, Action.ACCOUNT_DELETED, f"Compte supprimé. Motif : {reason}", member=member)
        delete_account(member)
    return {"username": member.username}


@router.post("/panel/members/{username}/admin", response=Done, auth=django_auth)
def set_admin(request, username: str, payload: AdminIn):
    """Nomme ou retire un administrateur. Réservé au propriétaire du site (superutilisateur)."""
    me = admin(request)
    if not me.is_superuser:
        raise HttpError(403, "Seul le propriétaire du site nomme les administrateurs.")
    member = member_for(me, username)
    if member.is_staff == payload.admin:
        return {"username": member.username}
    member.is_staff = payload.admin
    member.save(update_fields=["is_staff"])
    if payload.admin:
        log_action(me, Action.ADMIN_NAMED, "Devient administrateur du site.", member=member)
        notify(member, Kind.PROMOTION, "Tu es maintenant administrateur du site", "Le panneau Administration est dans le menu.", "/administration")
    else:
        log_action(me, Action.ADMIN_REMOVED, "N'est plus administrateur du site.", member=member)
    return {"username": member.username}


# ---------------------------------------------------------------- rôle

Role = Literal["nouveau", "membre", "relecteur", "expert", "moderateur", "administrateur"]

ROLE_LEVELS = {"nouveau": TL.NEW, "membre": TL.MEMBER, "relecteur": TL.REVIEWER, "expert": TL.EXPERT, "moderateur": TL.MODERATOR}
ROLE_LABELS = {
    "nouveau": "Nouveau",
    "membre": "Membre",
    "relecteur": "Relecteur",
    "expert": "Expert",
    "moderateur": "Modérateur",
    "administrateur": "Administrateur",
}


def role_of(member):
    """Le rôle tel que l'équipe le pense : administrateur, sinon le niveau de confiance."""
    if member.is_staff:
        return "administrateur"
    return next(role for role, level in ROLE_LEVELS.items() if level == member.trust_level)


class RoleIn(Schema):
    role: Role
    reason: str = Field(max_length=2000)


@router.post("/panel/members/{username}/role", response=Done, auth=django_auth)
def change_role(request, username: str, payload: RoleIn):
    """Un seul geste pour tout rôle, de Nouveau à Administrateur, au lieu de trois (niveau,
    modérateur, administrateur). Nommer ou retirer un administrateur reste réservé au
    propriétaire du site. Un niveau baissé à la main peut remonter tout seul si le membre en
    remplit de nouveau les conditions."""
    me = admin(request)
    member = member_for(me, username)
    reason = reason_of(payload.reason)
    before, after = role_of(member), payload.role
    if before == after:
        raise HttpError(409, f"Ce membre est déjà {ROLE_LABELS[after]}.")
    if "administrateur" in (before, after) and not me.is_superuser:
        raise HttpError(403, "Seul le propriétaire du site nomme ou retire un administrateur.")

    summary = f"{ROLE_LABELS[before]} → {ROLE_LABELS[after]}. Motif : {reason}"
    if after == "administrateur":
        action, url = Action.ADMIN_NAMED, "/administration"
    elif before == "administrateur":
        action, url = Action.ADMIN_REMOVED, "/progression"
    elif after == "moderateur":
        action, url = Action.MODERATOR_NAMED, "/moderation"
    elif before == "moderateur":
        action, url = Action.MODERATOR_REMOVED, "/progression"
    else:
        action, url = Action.TRUST_CHANGED, "/progression"
    with transaction.atomic():
        member.is_staff = after == "administrateur"
        if after != "administrateur":
            member.trust_level = ROLE_LEVELS[after]
        member.save(update_fields=["is_staff", "trust_level"])
        log_action(me, action, summary, member=member)
        notify(
            member,
            Kind.PROMOTION,
            f"Ton rôle sur XiMaths est maintenant : {ROLE_LABELS[after]}",
            f"Motif : {reason}",
            url,
            email=after in ("moderateur", "administrateur"),
        )
    return {"username": member.username}
