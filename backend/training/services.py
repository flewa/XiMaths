"""Entraînement chronométré, non classé.

Règles du document de conception :
- 15, 30, 45 ou 60 minutes, ou le temps conseillé ; tiers-temps ×1,33 ;
- le serveur fait foi : le temps ne compte que pendant que le navigateur donne
  signe de vie (sauvegarde toutes les 10 s) ; en entraînement, le chrono s'arrête
  donc si l'onglet se ferme, et la session se reprend ;
- deux pauses ; documents libres ;
- à l'échéance, la dernière version est rendue, avec 60 s de grâce pour le réseau ;
- au rendu : réponse finale vérifiée par SymPy, justification en relecture par les
  pairs, solutions débloquées, temps comparé à la médiane, auto-évaluation de 1 à 5.
"""

import statistics
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from config.errors import RuleError
from content.models import Exercise, Solution
from content.services import publish_solution

from .answers import check_answer
from .models import TimedSession

Status = TimedSession.Status

DURATIONS_MIN = (15, 30, 45, 60)
# Temps conseillé selon la difficulté, de 1 à 5.
RECOMMENDED_MIN = {1: 15, 2: 30, 3: 45, 4: 60, 5: 60}
EXTRA_TIME_FACTOR = 1.33
MAX_PAUSES = 2
# Au-delà de 30 s sans signe de vie, l'onglet est considéré fermé : ce temps ne compte pas.
HEARTBEAT_GAP = timedelta(seconds=30)
GRACE = timedelta(seconds=60)
MIN_SOLUTION_LENGTH = 20


def recommended_minutes(exercise):
    return RECOMMENDED_MIN[exercise.difficulty]


def _tick(session, now):
    """Ajoute au temps écoulé l'intervalle depuis le dernier signe de vie, s'il est court."""
    if session.status == Status.RUNNING and session.last_tick_at is not None:
        gap = now - session.last_tick_at
        if gap <= HEARTBEAT_GAP:
            session.elapsed_s += gap.total_seconds()
        session.last_tick_at = now


def remaining_s(session, now=None):
    """Secondes restantes, en comptant le temps depuis le dernier signe de vie."""
    elapsed = session.elapsed_s
    if session.status == Status.RUNNING and session.last_tick_at is not None:
        gap = (now or timezone.now()) - session.last_tick_at
        if gap <= HEARTBEAT_GAP:
            elapsed += gap.total_seconds()
    return session.limit_s - elapsed


@transaction.atomic
def start(user, exercise, *, minutes, now=None):
    """Démarre une session, ou reprend celle déjà ouverte sur cet exercice."""
    existing = TimedSession.objects.filter(user=user, exercise=exercise, status__in=[Status.RUNNING, Status.PAUSED]).first()
    if existing:
        return existing
    if minutes not in DURATIONS_MIN:
        raise RuleError("Durée possible : 15, 30, 45 ou 60 minutes.")
    if exercise.status != Exercise.Status.PUBLISHED:
        raise RuleError("L'exercice n'est pas publié.")
    if Solution.objects.filter(
        exercise=exercise,
        author=user,
        status__in=[Solution.Status.UNDER_REVIEW, Solution.Status.CONTESTED],
    ).exists():
        raise RuleError("Tu as déjà une solution en cours d'évaluation sur cet exercice.")
    now = now or timezone.now()
    try:
        with transaction.atomic():
            return TimedSession.objects.create(
                user=user,
                exercise=exercise,
                duration_s=minutes * 60,
                extra_time_factor=EXTRA_TIME_FACTOR if user.tiers_temps else 1.0,
                started_at=now,
                last_tick_at=now,
            )
    except IntegrityError:
        # Une autre requête vient d'ouvrir la session : on la reprend.
        return TimedSession.objects.get(user=user, exercise=exercise, status__in=[Status.RUNNING, Status.PAUSED])


def _require_open(session):
    if not session.open:
        raise RuleError("Cette session est terminée.")


@transaction.atomic
def save(session, *, draft, final_answer="", focus_losses=0, external_paste_chars=0, now=None):
    """Sauvegarde automatique, qui sert aussi de signe de vie. Après l'échéance et la
    grâce de 60 s, la sauvegarde est refusée et la dernière version est rendue."""
    now = now or timezone.now()
    _require_open(session)
    over = -remaining_s(session, now)
    _tick(session, now)
    if over <= GRACE.total_seconds():
        session.draft = draft
        session.final_answer = final_answer
    session.focus_losses += max(focus_losses, 0)
    session.external_paste_chars += max(external_paste_chars, 0)
    session.save()
    if over > 0:
        return submit(session, draft=session.draft, final_answer=session.final_answer, now=now)
    return session


@transaction.atomic
def pause(session, *, now=None):
    _require_open(session)
    if session.status == Status.PAUSED:
        return session
    if session.pauses_used >= MAX_PAUSES:
        raise RuleError("Tu as utilisé tes deux pauses.")
    now = now or timezone.now()
    _tick(session, now)
    session.status = Status.PAUSED
    session.last_tick_at = None
    session.pauses_used += 1
    session.save()
    return session


@transaction.atomic
def resume(session, *, now=None):
    _require_open(session)
    if session.status == Status.PAUSED:
        session.status = Status.RUNNING
    # Reprise après une pause, ou après un onglet fermé : on recompte à partir de maintenant.
    session.last_tick_at = now or timezone.now()
    session.save()
    return session


@transaction.atomic
def submit(session, *, draft, final_answer="", ai_usage=Solution.AiUsage.NONE, now=None):
    """Rend la session. La justification devient une solution, qui part en relecture."""
    _require_open(session)
    now = now or timezone.now()
    _tick(session, now)
    session.elapsed_s = min(session.elapsed_s, session.limit_s)
    session.draft = draft
    session.final_answer = final_answer.strip()
    session.answer_correct = (
        check_answer(session.final_answer, session.exercise.final_answer) if session.final_answer else None
    )
    session.status = Status.SUBMITTED
    session.submitted_at = now
    session.last_tick_at = None
    if len(draft.strip()) >= MIN_SOLUTION_LENGTH:
        solution = Solution.objects.create(
            exercise=session.exercise,
            author=session.user,
            body=draft.strip(),
            ai_usage=ai_usage,
            origin=Solution.Origin.TRAINING,
        )
        session.solution = publish_solution(solution, now=now)
    session.save()
    return session


@transaction.atomic
def abandon(session, *, now=None):
    _require_open(session)
    _tick(session, now or timezone.now())
    session.status = Status.ABANDONED
    session.last_tick_at = None
    session.save()
    return session


@transaction.atomic
def rate(session, rating):
    """Auto-évaluation de 1 à 5, une fois : elle affine la difficulté estimée."""
    if session.status != Status.SUBMITTED:
        raise RuleError("On évalue la difficulté après avoir rendu.")
    if session.self_rating is not None:
        raise RuleError("Tu as déjà évalué cet exercice.")
    if not 1 <= rating <= 5:
        raise RuleError("Note de 1 à 5.")
    session.self_rating = rating
    session.save(update_fields=["self_rating"])
    exercise = Exercise.objects.select_for_update().get(pk=session.exercise_id)
    count = exercise.difficulty_ratings
    previous = exercise.difficulty_estimated if exercise.difficulty_estimated is not None else 0
    exercise.difficulty_estimated = (previous * count + rating) / (count + 1)
    exercise.difficulty_ratings = count + 1
    exercise.save(update_fields=["difficulty_estimated", "difficulty_ratings", "updated_at"])
    return session


def median_elapsed_s(exercise, *, exclude=None):
    """Temps médian des sessions rendues sur cet exercice, ou None."""
    times = TimedSession.objects.filter(exercise=exercise, status=Status.SUBMITTED)
    if exclude is not None:
        times = times.exclude(pk=exclude.pk)
    values = list(times.values_list("elapsed_s", flat=True))
    return statistics.median(values) if values else None
