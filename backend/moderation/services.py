"""Signalements : dépôt par les membres, décision humaine et motivée, conséquences.

| Motif                | Cible                | Si le signalement est confirmé                           |
| doublon              | exercice             | tranché dans la file des doublons (fusion ou variantes)  |
| plagiat              | solution             | points annulés, −50, solution masquée                    |
| plagiat, inapproprié | exercice ou solution | contenu retiré, ses points annulés                       |
| IA non déclarée      | solution             | points annulés, sans étiquette publique ni pénalité      |
| erreur               | exercice ou solution | aucun effet automatique : le modérateur corrige          |

Un signalement confirmé de doublon, de plagiat ou d'erreur rapporte +3 à son auteur.
"""

import statistics
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from accounts.links import linked_ids
from accounts.permissions import is_moderator
from config import llm
from config.errors import RuleError
from content.models import Exercise, Solution
from content.services import assign_reviewers, award_author_points
from duplicates.models import DuplicatePair
from duplicates.services import open_reported_pair
from gamification.badges import check_badges
from gamification.models import PointTransaction
from gamification.services import apply_plagiarism, award, restore_points_from, reverse_points_from
from notifications.models import Notification
from notifications.services import notify

from . import comprehension
from .models import Appeal, ComprehensionQuestion, IntegritySignal, Report, Sanction

Kind = Notification.Kind

User = get_user_model()
Reason = Report.Reason
Status = Report.Status

REASONS_BY_TARGET = {
    "exercise": {Reason.DUPLICATE, Reason.PLAGIARISM, Reason.ERROR, Reason.INAPPROPRIATE},
    "solution": {Reason.PLAGIARISM, Reason.ERROR, Reason.INAPPROPRIATE, Reason.UNDECLARED_AI},
}
REWARDED_REASONS = {Reason.DUPLICATE, Reason.PLAGIARISM, Reason.ERROR}
# Signaler un doublon est un droit du niveau Relecteur.
DUPLICATE_MIN_TRUST = User.TrustLevel.REVIEWER
PAIR_OUTCOMES = {
    DuplicatePair.Status.MERGED: (True, "Exercices fusionnés par la modération."),
    DuplicatePair.Status.VARIANTS: (True, "Exercices liés comme variantes par la modération."),
    DuplicatePair.Status.DISTINCT: (False, "Exercices jugés distincts par la modération."),
}


@transaction.atomic
def create_report(reporter, *, reason, exercise=None, solution=None, details="", duplicate_of=None):
    target = exercise or solution
    kind = "exercise" if exercise else "solution"
    if reason not in REASONS_BY_TARGET[kind]:
        raise RuleError("Ce motif ne s'applique pas à ce contenu.")
    if target.author_id == reporter.pk:
        raise PermissionDenied("On ne signale pas sa propre contribution.")
    pair = None
    if reason == Reason.DUPLICATE:
        if reporter.trust_level < DUPLICATE_MIN_TRUST and not is_moderator(reporter):
            raise PermissionDenied("Les doublons se signalent à partir du niveau Relecteur.")
        if duplicate_of is None or duplicate_of.pk == exercise.pk:
            raise RuleError("Indique l'exercice dont celui-ci est le doublon.")
        pair = open_reported_pair(exercise, duplicate_of)
    try:
        with transaction.atomic():
            return Report.objects.create(
                reporter=reporter,
                exercise=exercise,
                solution=solution,
                reason=reason,
                details=details.strip(),
                duplicate_pair=pair,
            )
    except IntegrityError:
        raise RuleError("Tu as déjà signalé ce contenu pour ce motif.")


def _settle(report, *, confirmed, moderator, note, now):
    report.status = Status.CONFIRMED if confirmed else Status.REJECTED
    report.decided_by = moderator
    report.decided_at = now
    report.decision_note = note
    report.save()
    rewarded = confirmed and report.reason in REWARDED_REASONS
    if rewarded:
        level = (report.exercise or report.solution.exercise).primary_level
        award(report.reporter, PointTransaction.Reason.REPORT_CONFIRMED, report, level=level, now=now)
    check_badges(report.reporter, now=now)
    notify(
        report.reporter,
        Kind.REPORT_RESOLVED,
        "Ton signalement est confirmé" if confirmed else "Ton signalement n'a pas été retenu",
        "Merci : +3 points." if rewarded else "Merci d'avoir pris le temps de signaler.",
        "/signalements",
        now=now,
    )


def _apply(report, *, note, now):
    """Conséquences d'un signalement confirmé sur le contenu visé. Tout retrait est
    motivé auprès de son auteur, qui peut faire appel."""
    removed = None
    if report.solution is not None:
        solution = report.solution
        if report.reason == Reason.PLAGIARISM:
            apply_plagiarism(solution, now=now)
        elif report.reason in (Reason.INAPPROPRIATE, Reason.UNDECLARED_AI):
            reverse_points_from(solution, now=now)
        if report.reason in (Reason.PLAGIARISM, Reason.INAPPROPRIATE):
            solution.status = Solution.Status.HIDDEN
            solution.save(update_fields=["status", "updated_at"])
            removed = (solution.author, f"ta solution de « {solution.exercise.title} »")
        elif report.reason == Reason.UNDECLARED_AI:
            removed = (solution.author, None)
    elif report.reason in (Reason.PLAGIARISM, Reason.INAPPROPRIATE):
        exercise = report.exercise
        reverse_points_from(exercise, now=now)
        exercise.status = Exercise.Status.REMOVED
        exercise.save(update_fields=["status", "updated_at"])
        removed = (exercise.author, f"ton exercice « {exercise.title} »")
    # Erreur : le modérateur corrige le contenu lui-même.
    if removed:
        author, what = removed
        notify(
            author,
            Kind.CONTENT_REMOVED,
            f"La modération a retiré {what}" if what else "La modération a annulé des points",
            f"Motif : {note}\n\nTu peux faire appel sous 14 jours depuis la page Mes décisions.",
            "/decisions",
            now=now,
        )


@transaction.atomic
def resolve_report(report, *, confirmed, moderator, note="", now=None):
    """Tranche un signalement (hors doublon). Les autres signalements ouverts du même
    contenu pour le même motif sont tranchés de la même façon."""
    if not is_moderator(moderator):
        raise PermissionDenied("Seuls les modérateurs traitent les signalements.")
    if report.status != Status.OPEN:
        raise RuleError("Ce signalement est déjà traité.")
    if report.reason == Reason.DUPLICATE:
        raise RuleError("Un doublon se tranche dans la file des doublons.")
    note = note.strip()
    if confirmed and not note:
        raise RuleError("Motive la décision : le motif est communiqué à l'auteur du contenu.")
    now = now or timezone.now()
    if confirmed:
        _apply(report, note=note, now=now)
    same = Report.objects.filter(
        status=Status.OPEN, reason=report.reason, exercise=report.exercise, solution=report.solution
    )
    for each in same.select_related("reporter", "exercise", "solution__exercise"):
        _settle(each, confirmed=confirmed, moderator=moderator, note=note, now=now)
    report.refresh_from_db()
    return report


def settle_duplicate_reports(sender, pair, moderator, **kwargs):
    """Reçoit duplicates.signals.pair_decided : les signalements de doublon de la paire
    suivent la décision prise dans la file des doublons."""
    outcome = PAIR_OUTCOMES.get(pair.status)
    if outcome is None:
        return
    confirmed, note = outcome
    for report in pair.reports.filter(status=Status.OPEN).select_related("reporter", "exercise"):
        _settle(report, confirmed=confirmed, moderator=moderator, note=note, now=pair.decided_at)


# ---------------------------------------------------------------- signaux d'intégrité


def answer_signal(signal, user, text):
    """Réponse de l'auteur à la question neutre, lue par le modérateur."""
    if signal.user_id != user.pk:
        raise PermissionDenied("Cette question ne te concerne pas.")
    if signal.status != IntegritySignal.Status.OPEN:
        raise RuleError("Cette vérification est déjà close.")
    signal.author_answer = text.strip()
    signal.save(update_fields=["author_answer"])
    return signal


@transaction.atomic
def decide_signal(signal, *, confirmed, moderator, note="", now=None):
    """Lève le signal (la solution part en relecture) ou confirme le plagiat
    (points annulés, −50, solution masquée, motif envoyé à l'auteur)."""
    if not is_moderator(moderator):
        raise PermissionDenied("Seuls les modérateurs tranchent.")
    if signal.status != IntegritySignal.Status.OPEN:
        raise RuleError("Ce signal est déjà tranché.")
    note = note.strip()
    if confirmed and not note:
        raise RuleError("Motive la décision : le motif est communiqué à l'auteur.")
    now = now or timezone.now()
    solution = signal.solution
    signal.status = IntegritySignal.Status.CONFIRMED if confirmed else IntegritySignal.Status.CLEARED
    signal.decided_by = moderator
    signal.decided_at = now
    signal.decision_note = note
    signal.save()
    if solution is None or solution.status != Solution.Status.HELD:
        return signal
    if confirmed:
        apply_plagiarism(solution, now=now)
        solution.status = Solution.Status.HIDDEN
        solution.save(update_fields=["status", "updated_at"])
        notify(
            solution.author,
            Kind.CONTENT_REMOVED,
            f"La modération a retiré ta solution de « {solution.exercise.title} »",
            f"Motif : {note}\n\nTu peux faire appel sous 14 jours depuis la page Mes décisions.",
            "/decisions",
            now=now,
        )
    else:
        solution.status = Solution.Status.UNDER_REVIEW
        solution.save(update_fields=["status", "updated_at"])
        assign_reviewers(solution, now=now)
    return signal


def purge_signals(*, now=None):
    """Les signaux tranchés s'effacent un an après la décision."""
    limit = (now or timezone.now()) - timedelta(days=365)
    return IntegritySignal.objects.exclude(status=IntegritySignal.Status.OPEN).filter(decided_at__lt=limit).delete()[0]


# ---------------------------------------------------------------- sanctions et appels

SANCTION_DURATIONS = {
    Sanction.Kind.LEADERBOARD_BAN: timedelta(days=30),
    Sanction.Kind.SUSPENSION: timedelta(days=7),
}
APPEAL_WINDOW = timedelta(days=14)
APPEAL_RESPONSE = timedelta(days=7)
SANCTION_TEXT = {
    Sanction.Kind.WARNING: "Avertissement",
    Sanction.Kind.LEADERBOARD_BAN: "Exclusion des classements pendant 30 jours",
    Sanction.Kind.SUSPENSION: "Suspension du compte pendant 7 jours",
    Sanction.Kind.BAN: "Bannissement",
}


def active_sanctions(user, *, now=None):
    now = now or timezone.now()
    return Sanction.objects.filter(user=user, lifted_at=None).filter(Q(ends_at=None) | Q(ends_at__gt=now))


def _restore_status(user, *, now):
    """Statut du compte d'après les sanctions encore actives."""
    kinds = set(active_sanctions(user, now=now).values_list("kind", flat=True))
    if Sanction.Kind.BAN in kinds:
        status = User.Status.BANNED
    elif Sanction.Kind.SUSPENSION in kinds:
        status = User.Status.SUSPENDED
    else:
        status = User.Status.ACTIVE
    if user.status != status:
        user.status = status
        user.save(update_fields=["status"])


@transaction.atomic
def sanction(user, kind, *, reason, moderator, report=None, now=None):
    """Applique une sanction, motivée et notifiée ; le membre peut faire appel."""
    if not is_moderator(moderator):
        raise PermissionDenied("Seuls les modérateurs sanctionnent.")
    if not reason.strip():
        raise RuleError("Motive la sanction : type de signal, contenus concernés.")
    now = now or timezone.now()
    duration = SANCTION_DURATIONS.get(kind)
    decision = Sanction.objects.create(
        user=user,
        kind=kind,
        reason=reason.strip(),
        report=report,
        starts_at=now,
        ends_at=now + duration if duration else None,
        decided_by=moderator,
    )
    _restore_status(user, now=now)
    notify(
        user,
        Kind.SANCTION,
        f"Décision de modération : {SANCTION_TEXT[kind].lower()}",
        f"Motif : {decision.reason}\n\nTu peux faire appel sous 14 jours depuis la page Mes décisions.",
        "/decisions",
        now=now,
    )
    return decision


def lift(decision, *, reason, now=None):
    now = now or timezone.now()
    decision.lifted_at = now
    decision.lifted_reason = reason
    decision.save(update_fields=["lifted_at", "lifted_reason"])
    _restore_status(decision.user, now=now)
    return decision


def lift_expired(*, now=None):
    """Fin des sanctions à durée : le compte retrouve son statut. Renvoie leur nombre."""
    now = now or timezone.now()
    expired = list(Sanction.objects.filter(lifted_at=None, ends_at__lte=now).select_related("user"))
    for decision in expired:
        lift(decision, reason="Durée écoulée.", now=now)
    return len(expired)


def _decision_facts(decision):
    """(membre concerné, date de la décision, modérateur) d'une décision contestable."""
    if isinstance(decision, Sanction):
        return decision.user_id, decision.created_at, decision.decided_by_id
    if isinstance(decision, Report):
        content = decision.exercise or decision.solution
        return content.author_id, decision.decided_at, decision.decided_by_id
    return decision.user_id, decision.decided_at, decision.decided_by_id


@transaction.atomic
def create_appeal(user, decision, statement, *, now=None):
    """Appel d'une sanction, d'un retrait de contenu ou d'un plagiat confirmé."""
    owner, decided_at, _ = _decision_facts(decision)
    if owner != user.pk:
        raise PermissionDenied("Cette décision ne te concerne pas.")
    if isinstance(decision, Report) and decision.status != Report.Status.CONFIRMED:
        raise RuleError("Seul un retrait confirmé peut faire l'objet d'un appel.")
    if isinstance(decision, IntegritySignal) and decision.status != IntegritySignal.Status.CONFIRMED:
        raise RuleError("Seul un plagiat confirmé peut faire l'objet d'un appel.")
    now = now or timezone.now()
    if decided_at is None or now - decided_at > APPEAL_WINDOW:
        raise RuleError("Le délai d'appel de 14 jours est dépassé.")
    if not statement.strip():
        raise RuleError("Explique en quelques mots pourquoi la décision te semble injuste.")
    field = {Sanction: "sanction", Report: "report", IntegritySignal: "signal"}[type(decision)]
    try:
        with transaction.atomic():
            return Appeal.objects.create(user=user, statement=statement.strip(), **{field: decision})
    except IntegrityError:
        raise RuleError("Tu as déjà fait appel de cette décision.")


def _restore_content(decision, *, now):
    """Appel accepté sur un retrait : le contenu revient, avec ses points."""
    if isinstance(decision, IntegritySignal):
        solution = decision.solution
        restore_points_from(solution, now=now)
        solution.status = Solution.Status.UNDER_REVIEW
        solution.save(update_fields=["status", "updated_at"])
        assign_reviewers(solution, now=now)
        return
    if decision.exercise_id:
        exercise = decision.exercise
        if exercise.status == Exercise.Status.REMOVED:
            restore_points_from(exercise, now=now)
            exercise.status = Exercise.Status.PUBLISHED
            exercise.save(update_fields=["status", "updated_at"])
        return
    solution = decision.solution
    restore_points_from(solution, now=now)
    if solution.status == Solution.Status.HIDDEN:
        solution.status = Solution.Status.VALIDATED if solution.validated_at else Solution.Status.UNDER_REVIEW
        solution.save(update_fields=["status", "updated_at"])


@transaction.atomic
def decide_appeal(appeal, *, overturn, moderator, note, now=None):
    """Un autre modérateur que l'auteur de la décision tranche l'appel, avec un motif."""
    if not is_moderator(moderator):
        raise PermissionDenied("Seuls les modérateurs examinent les appels.")
    _, _, original = _decision_facts(appeal.decision)
    if original == moderator.pk:
        raise PermissionDenied("Un appel est examiné par un autre modérateur que l'auteur de la décision.")
    if appeal.status != Appeal.Status.PENDING:
        raise RuleError("Cet appel est déjà tranché.")
    if not note.strip():
        raise RuleError("Motive la décision d'appel.")
    now = now or timezone.now()
    appeal.status = Appeal.Status.OVERTURNED if overturn else Appeal.Status.UPHELD
    appeal.decided_by = moderator
    appeal.decided_at = now
    appeal.decision_note = note.strip()
    appeal.save()
    if overturn:
        decision = appeal.decision
        if isinstance(decision, Sanction):
            lift(decision, reason="Annulée en appel.", now=now)
        else:
            _restore_content(decision, now=now)
    notify(
        appeal.user,
        Kind.APPEAL_DECIDED,
        "Ton appel est accepté : la décision est annulée" if overturn else "Ton appel n'est pas retenu",
        f"Motif : {appeal.decision_note}",
        "/decisions",
        now=now,
    )
    return appeal


def appeal_stats():
    """Garde-fou du document : plus de 20 % de décisions annulées en appel signifie des
    seuils trop agressifs. Aussi : délai médian de traitement des signalements."""
    decided = Appeal.objects.exclude(status=Appeal.Status.PENDING)
    total = decided.count()
    overturned = decided.filter(status=Appeal.Status.OVERTURNED).count()
    delays = [
        (decided_at - created_at).total_seconds() / 3600
        for created_at, decided_at in Report.objects.exclude(decided_at=None).values_list("created_at", "decided_at")
    ]
    return {
        "appels_tranches": total,
        "taux_annulation": overturned / total if total else None,
        "delai_median_signalement_h": statistics.median(delays) if delays else None,
    }


# ---------------------------------------------------------------- questions de compréhension

Question = ComprehensionQuestion.Status


def _own_question(question, user):
    if question.user_id != user.pk:
        raise PermissionDenied("Cette question ne t'est pas adressée.")


@transaction.atomic
def open_question(question, user, *, now=None):
    """Le membre ouvre la question : les 5 minutes commencent, côté serveur."""
    _own_question(question, user)
    now = now or timezone.now()
    if question.status == Question.OPENED:
        return question
    if question.status != Question.SENT:
        raise RuleError("Cette question n'est plus ouverte.")
    if now - question.sent_at > comprehension.OPEN_WITHIN:
        raise RuleError("Le délai de 72 heures pour ouvrir cette question est passé.")
    question.status = Question.OPENED
    question.opened_at = now
    question.save(update_fields=["status", "opened_at"])
    return question


def answer_deadline(question):
    return question.opened_at + comprehension.ANSWER_WITHIN if question.opened_at else None


@transaction.atomic
def answer_question(question, user, text, *, now=None):
    _own_question(question, user)
    now = now or timezone.now()
    if question.status != Question.OPENED:
        raise RuleError("Ouvre d'abord la question, ou elle est déjà close.")
    if now > answer_deadline(question) + comprehension.GRACE:
        raise RuleError("Les 5 minutes sont écoulées.")
    if not text.strip():
        raise RuleError("Écris ta réponse, même courte.")
    question.answer = text.strip()
    question.answered_at = now
    question.status = Question.ANSWERED
    question.save(update_fields=["answer", "answered_at", "status"])
    return question


def release_points(solution, *, now=None):
    """Question réussie, ou jamais posée : les points retenus sont accordés."""
    now = now or timezone.now()
    session = getattr(solution, "timed_session", None)
    if session is not None and session.challenge_id and session.answer_points:
        award(
            solution.author,
            PointTransaction.Reason.CHALLENGE_ANSWER,
            session,
            amount=session.answer_points,
            level=solution.exercise.primary_level,
            now=now,
        )
    if solution.status == Solution.Status.VALIDATED:
        award_author_points(solution, now=now)


def can_evaluate(user, question):
    return (
        (user.trust_level >= User.TrustLevel.EXPERT or is_moderator(user))
        and question.user_id != user.pk
        and question.user_id not in linked_ids(user)
    )


@transaction.atomic
def evaluate_question(question, *, passed, evaluator, note="", now=None):
    """Décision humaine, motivée. Réussie : points accordés et 30 jours sans question ;
    insuffisante : la solution reste publiée, sans ses points de classement."""
    if not can_evaluate(evaluator, question):
        raise PermissionDenied("Un relecteur de niveau 3 ou un modérateur, sans lien avec l'auteur, évalue.")
    if question.status != Question.ANSWERED:
        raise RuleError("Il n'y a pas de réponse à évaluer.")
    now = now or timezone.now()
    question.status = Question.PASSED if passed else Question.FAILED
    question.evaluated_by = evaluator
    question.evaluated_at = now
    question.evaluation_note = note.strip()
    question.save(update_fields=["status", "evaluated_by", "evaluated_at", "evaluation_note"])
    if passed:
        release_points(question.solution, now=now)
    notify(
        question.user,
        Kind.COMPREHENSION_QUESTION,
        "Ta réponse est validée" if passed else "Ta réponse n'a pas suffi",
        "Merci : les points de ta solution sont accordés."
        if passed
        else "Ta solution reste publiée, mais ses points de classement ne sont pas accordés. "
        "Ce n'est pas une sanction.",
        "/questions",
        email=False,
        now=now,
    )
    return question


def comprehension_tick(*, now=None):
    """Tâche horaire : rédige les questions avec Claude s'il est configuré, abandonne
    celles que personne n'a rédigées sous 72 h (les points sont alors accordés), clôt
    les délais dépassés, et prépare l'évaluation des réponses."""
    now = now or timezone.now()
    done = 0
    for question in ComprehensionQuestion.objects.filter(status=Question.TO_WRITE).select_related(
        "solution__exercise", "user"
    ):
        if llm.enabled() and comprehension.write_with_llm(question):
            comprehension.send(question, now=now)
        elif now - question.created_at > comprehension.WRITE_WITHIN:
            question.status = Question.DROPPED
            question.save(update_fields=["status"])
            release_points(question.solution, now=now)
        else:
            continue
        done += 1
    late_opening = Q(status=Question.SENT, sent_at__lt=now - comprehension.OPEN_WITHIN)
    late_answer = Q(
        status=Question.OPENED, opened_at__lt=now - comprehension.ANSWER_WITHIN - comprehension.GRACE
    )
    done += ComprehensionQuestion.objects.filter(late_opening | late_answer).update(status=Question.EXPIRED)
    if llm.enabled():
        for question in ComprehensionQuestion.objects.filter(
            status=Question.ANSWERED, llm_assessment=""
        ).select_related("solution__exercise"):
            comprehension.preassess_with_llm(question)
    return done
