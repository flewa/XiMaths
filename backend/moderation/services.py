"""Signalements : dépôt par les membres, décision humaine et motivée, conséquences.

| Motif                | Cible                | Si le signalement est confirmé                           |
| doublon              | exercice             | tranché dans la file des doublons (fusion ou variantes)  |
| plagiat              | solution             | points annulés, −50, solution masquée                    |
| plagiat, inapproprié | exercice ou solution | contenu retiré, ses points annulés                       |
| IA non déclarée      | solution             | points annulés, sans étiquette publique ni pénalité      |
| erreur               | exercice ou solution | aucun effet automatique : le modérateur corrige          |

Un signalement confirmé de doublon, de plagiat ou d'erreur rapporte +3 à son auteur.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.permissions import is_moderator
from config.errors import RuleError
from content.models import Exercise, Solution
from duplicates.models import DuplicatePair
from duplicates.services import open_reported_pair
from gamification.badges import check_badges
from gamification.models import PointTransaction
from gamification.services import apply_plagiarism, award, reverse_points_from

from .models import Report

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
    if confirmed and report.reason in REWARDED_REASONS:
        level = (report.exercise or report.solution.exercise).primary_level
        award(report.reporter, PointTransaction.Reason.REPORT_CONFIRMED, report, level=level, now=now)
    check_badges(report.reporter, now=now)


def _apply(report, *, now):
    """Conséquences d'un signalement confirmé sur le contenu visé."""
    if report.solution is not None:
        solution = report.solution
        if report.reason == Reason.PLAGIARISM:
            apply_plagiarism(solution, now=now)
        elif report.reason in (Reason.INAPPROPRIATE, Reason.UNDECLARED_AI):
            reverse_points_from(solution, now=now)
        if report.reason in (Reason.PLAGIARISM, Reason.INAPPROPRIATE):
            solution.status = Solution.Status.HIDDEN
            solution.save(update_fields=["status", "updated_at"])
    elif report.reason in (Reason.PLAGIARISM, Reason.INAPPROPRIATE):
        exercise = report.exercise
        reverse_points_from(exercise, now=now)
        exercise.status = Exercise.Status.REMOVED
        exercise.save(update_fields=["status", "updated_at"])
    # Erreur : le modérateur corrige le contenu lui-même.


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
        _apply(report, now=now)
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
