"""Entraînement chronométré, non classé.

Règles du document de conception :
- 15, 30, 45 ou 60 minutes, ou le temps conseillé ;
- le serveur fait foi : le temps ne compte que pendant que le navigateur donne
  signe de vie (sauvegarde toutes les 10 s) ; en entraînement, le chrono s'arrête
  donc si l'onglet se ferme, et la session se reprend ;
- deux pauses ; documents libres ;
- la copie est manuscrite : on la photographie depuis le téléphone (QR code) pendant le
  temps imparti, avec 60 s de grâce pour le réseau ; à l'échéance, ce qui est arrivé est
  rendu ;
- au rendu : copie en relecture par les pairs, solutions débloquées, temps comparé à la
  médiane, auto-évaluation de 1 à 5.

Le défi du jour (challenges.py) passe par les mêmes sessions, avec ses propres règles :
le chrono compte depuis le départ, sans pause, et la session rapporte des points.
"""

import statistics
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from config.errors import RuleError
from content import photos
from content.models import Exercise, PhotoUpload, Solution
from content.services import publish_solution
from gamification.badges import check_badges

from . import challenges
from .models import TimedSession

Status = TimedSession.Status

DURATIONS_MIN = (15, 30, 45, 60)
# Temps conseillé selon la difficulté, de 1 à 5.
RECOMMENDED_MIN = {1: 15, 2: 30, 3: 45, 4: 60, 5: 60}
MAX_PAUSES = 2
# Au-delà de 30 s sans signe de vie, l'onglet est considéré fermé : ce temps ne compte pas.
HEARTBEAT_GAP = timedelta(seconds=30)
GRACE = timedelta(seconds=60)


def recommended_minutes(exercise):
    return RECOMMENDED_MIN[exercise.difficulty]


def _tick(session, now):
    """Ajoute au temps écoulé l'intervalle depuis le dernier signe de vie, s'il est court.
    En défi, le chrono ne s'arrête jamais : le temps écoulé part du départ."""
    if session.ranked:
        session.elapsed_s = (now - session.started_at).total_seconds()
        return
    if session.status == Status.RUNNING and session.last_tick_at is not None:
        gap = now - session.last_tick_at
        if gap <= HEARTBEAT_GAP:
            session.elapsed_s += gap.total_seconds()
        session.last_tick_at = now


def remaining_s(session, now=None):
    """Secondes restantes, en comptant le temps depuis le dernier signe de vie."""
    if session.ranked:
        return session.limit_s - ((now or timezone.now()) - session.started_at).total_seconds()
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
        status=Solution.Status.UNDER_REVIEW,
    ).exists():
        raise RuleError("Tu as déjà une solution en cours d'évaluation sur cet exercice.")
    now = now or timezone.now()
    try:
        with transaction.atomic():
            return TimedSession.objects.create(
                user=user,
                exercise=exercise,
                duration_s=minutes * 60,
                started_at=now,
                last_tick_at=now,
            )
    except IntegrityError:
        # Une autre requête vient d'ouvrir la session : on la reprend.
        return TimedSession.objects.get(user=user, exercise=exercise, status__in=[Status.RUNNING, Status.PAUSED])


def _require_open(session):
    if not session.open:
        raise RuleError("Cette session est terminée.")


def accepts_photos(session, now=None):
    """Le téléphone peut-il encore déposer une photo ? Pendant le temps imparti et la
    grâce de 60 s, tant que la session n'est pas rendue."""
    return session.open and remaining_s(session, now) > -GRACE.total_seconds()


@transaction.atomic
def photo_upload(session, *, now=None):
    """L'envoi de photos de la session : son jeton, dans le QR code affiché dès le départ."""
    _require_open(session)
    if session.photo_upload_id:
        return session.photo_upload
    now = now or timezone.now()
    upload = photos.open_upload(session.user, session.exercise, now=now)
    # Indicatif : c'est l'état de la session qui ouvre ou ferme le dépôt.
    upload.expires_at = session.started_at + timedelta(seconds=session.limit_s) + GRACE
    upload.save(update_fields=["expires_at"])
    session.photo_upload = upload
    session.save(update_fields=["photo_upload"])
    return upload


@transaction.atomic
def save(session, *, focus_losses=0, now=None):
    """Signe de vie, toutes les 10 s : il fait avancer le chrono. Après l'échéance et
    la grâce de 60 s, la session est rendue avec les photos arrivées."""
    now = now or timezone.now()
    _require_open(session)
    over = -remaining_s(session, now)
    _tick(session, now)
    session.focus_losses += max(focus_losses, 0)
    session.save()
    if over > GRACE.total_seconds():
        return submit(session, now=now)
    return session


@transaction.atomic
def pause(session, *, now=None):
    _require_open(session)
    if session.status == Status.PAUSED:
        return session
    if session.ranked:
        raise RuleError("Pas de pause pendant un défi : le chrono continue.")
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
def submit(session, *, ai_usage=Solution.AiUsage.NONE, now=None):
    """Rend la session. Les photos arrivées deviennent une solution, qui part en relecture ;
    sans photo, rien n'est envoyé."""
    _require_open(session)
    now = now or timezone.now()
    _tick(session, now)
    session.elapsed_s = min(session.elapsed_s, session.limit_s)
    session.status = Status.SUBMITTED
    session.submitted_at = now
    session.last_tick_at = None
    if session.ranked:
        challenges.score(session)
    # Enregistrée avant la publication : le score d'intégrité lit le temps de la session.
    session.save()
    upload = PhotoUpload.objects.filter(pk=session.photo_upload_id).first()
    if upload is not None and photos.pending(upload).exists():
        solution = Solution.objects.create(
            exercise=session.exercise,
            author=session.user,
            # L'IA est interdite en défi.
            ai_usage=Solution.AiUsage.NONE if session.ranked else ai_usage,
            origin=Solution.Origin.DAILY if session.ranked else Solution.Origin.TRAINING,
            variant_statement=challenges.statement(session) if session.ranked else "",
        )
        photos.attach(upload, solution)
        session.solution = solution
        session.save(update_fields=["solution"])
        publish_solution(solution, now=now)
    if session.ranked:
        check_badges(session.user, now=now)
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


def close_expired(*, now=None):
    """Défis dont l'échéance et la grâce sont passées sans rendu (onglet fermé) : les
    photos arrivées sont rendues. Renvoie leur nombre."""
    now = now or timezone.now()
    count = 0
    running = TimedSession.objects.filter(status=Status.RUNNING, challenge__isnull=False).select_related(
        "exercise", "challenge__template", "user"
    )
    for session in running:
        if -remaining_s(session, now) > GRACE.total_seconds():
            submit(session, now=now)
            count += 1
    return count


def median_elapsed_s(exercise, *, exclude=None):
    """Temps médian des sessions rendues sur cet exercice, ou None."""
    times = TimedSession.objects.filter(exercise=exercise, status=Status.SUBMITTED)
    if exclude is not None:
        times = times.exclude(pk=exclude.pk)
    values = list(times.values_list("elapsed_s", flat=True))
    return statistics.median(values) if values else None
