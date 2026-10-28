"""Série hebdomadaire et objectifs personnels, sans dark patterns.

- Objectif choisi : de 2 à 7 jours actifs par semaine. Un jour actif suppose une
  action réelle : une tentative de solution, une relecture, ou 15 minutes de
  chronomètre ; une simple connexion ne compte pas.
- Deux jokers par mois s'appliquent d'eux-mêmes à une semaine manquée.
- Le mode examens ou vacances suspend la série, 4 semaines au plus.
- La régularité rapporte des badges (Régulier), jamais de points.
"""

from collections import defaultdict
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils import timezone

from config.errors import RuleError
from content.models import Review, Solution
from notifications.models import Notification
from notifications.services import notify
from training.models import TimedSession

from .badges import check_badges
from .models import Goal, WeeklyStreak
from .rankings import Week

User = get_user_model()
Status = WeeklyStreak.Status

TIMED_ACTIVE_S = 15 * 60
JOKERS_PER_MONTH = 2
MAX_VACATION = timedelta(weeks=4)
# Une semaine « tenue » prolonge la série ; les vacances la suspendent sans la casser.
KEPT = {Status.ACHIEVED, Status.JOKER}


def active_days(user, start, end):
    """Jours (dates locales) avec une action réelle entre `start` et `end`."""
    days = set()
    attempts = Solution.objects.filter(author=user, created_at__gte=start, created_at__lt=end).exclude(
        status=Solution.Status.DRAFT
    )
    days.update(timezone.localdate(moment) for moment in attempts.values_list("created_at", flat=True))
    reviews = Review.objects.filter(reviewer=user, submitted_at__gte=start, submitted_at__lt=end)
    days.update(timezone.localdate(moment) for moment in reviews.values_list("submitted_at", flat=True))
    timed = defaultdict(float)
    for started_at, elapsed in TimedSession.objects.filter(
        user=user, started_at__gte=start, started_at__lt=end
    ).values_list("started_at", "elapsed_s"):
        timed[timezone.localdate(started_at)] += elapsed
    days.update(day for day, seconds in timed.items() if seconds >= TIMED_ACTIVE_S)
    return days


def on_vacation(user, week):
    """La semaine chevauche-t-elle le mode examens ou vacances ?"""
    return bool(
        user.vacation_from
        and user.vacation_until
        and user.vacation_from <= week.sunday
        and user.vacation_until >= week.monday
    )


def jokers_used(user, month_start):
    """Jokers consommés dans le mois de `month_start` (une semaine compte pour le mois de son lundi)."""
    return sum(
        1
        for label in WeeklyStreak.objects.filter(user=user, status=Status.JOKER).values_list("week", flat=True)
        if (monday := Week.parse(label).monday).year == month_start.year and monday.month == month_start.month
    )


def streak_length(user, *, before=None):
    """Semaines tenues d'affilée, en remontant depuis la dernière semaine close."""
    length = 0
    records = WeeklyStreak.objects.filter(user=user)
    if before is not None:
        records = records.filter(week__lt=before.label)
    for status in records.order_by("-week").values_list("status", flat=True):
        if status == Status.MISSED:
            break
        if status in KEPT:
            length += 1
    return length


def _record(user, week, now):
    """Bilan d'une semaine close, ou None si rien ne justifie de l'enregistrer."""
    days = len(active_days(user, week.start, week.end))
    goal = user.weekly_goal_days
    if on_vacation(user, week):
        status = Status.VACATION
    elif days >= goal:
        status = Status.ACHIEVED
    elif streak_length(user, before=week) == 0:
        # Pas de série à protéger : une semaine sans activité n'est pas enregistrée,
        # une semaine active en dessous de l'objectif l'est, comme manquée.
        if days == 0:
            return None
        status = Status.MISSED
    elif jokers_used(user, week.monday) < JOKERS_PER_MONTH:
        status = Status.JOKER
    else:
        status = Status.MISSED
    try:
        with transaction.atomic():
            return WeeklyStreak.objects.create(user=user, week=week.label, goal=goal, active_days=days, status=status)
    except IntegrityError:
        return None  # déjà close


SUMMARY = {
    Status.ACHIEVED: "Objectif atteint : {days} jours actifs sur {goal}.",
    Status.JOKER: "{days} jours actifs sur {goal} : un joker a protégé ta série.",
    Status.VACATION: "Semaine en mode examens ou vacances : ta série est en pause.",
    Status.MISSED: "{days} jours actifs sur {goal} cette semaine.",
}


def close_week(week, *, now=None):
    """Clôt `week` pour chaque membre concerné : actif cette semaine-là, ou avec une
    série à poursuivre. Idempotent. Renvoie le nombre de bilans créés."""
    now = now or timezone.now()
    previous = week.shifted(-1).label
    candidates = User.objects.filter(is_active=True).filter(
        pk__in=set(Solution.objects.filter(created_at__gte=week.start, created_at__lt=week.end).values_list("author", flat=True))
        | set(Review.objects.filter(submitted_at__gte=week.start, submitted_at__lt=week.end).values_list("reviewer", flat=True))
        | set(TimedSession.objects.filter(started_at__gte=week.start, started_at__lt=week.end).values_list("user", flat=True))
        | set(WeeklyStreak.objects.filter(week=previous).exclude(status=Status.MISSED).values_list("user", flat=True))
    )
    created = 0
    for user in candidates:
        record = _record(user, week, now)
        if record is None:
            continue
        created += 1
        check_badges(user, now=now)
        notify(
            user,
            Notification.Kind.GOAL,
            "Ta semaine en bref",
            SUMMARY[record.status].format(days=record.active_days, goal=record.goal),
            "/progression",
            now=now,
        )
    return created


def set_goal(user, days):
    if not 2 <= days <= 7:
        raise RuleError("Objectif de 2 à 7 jours actifs par semaine.")
    user.weekly_goal_days = days
    user.save(update_fields=["weekly_goal_days"])


def start_vacation(user, until, *, today=None):
    today = today or timezone.localdate()
    if until < today:
        raise RuleError("La fin du mode examens ou vacances est déjà passée.")
    if until - today > MAX_VACATION:
        raise RuleError("Le mode examens ou vacances dure 4 semaines au plus.")
    user.vacation_from = today
    user.vacation_until = until
    user.save(update_fields=["vacation_from", "vacation_until"])


def end_vacation(user, *, today=None):
    """Fin anticipée : les jours déjà passés en vacances restent couverts."""
    today = today or timezone.localdate()
    if not current_vacation(user, today):
        return
    if user.vacation_from >= today:
        user.vacation_from = user.vacation_until = None
    else:
        user.vacation_until = today - timedelta(days=1)
    user.save(update_fields=["vacation_from", "vacation_until"])


def current_vacation(user, today=None):
    today = today or timezone.localdate()
    if user.vacation_until and user.vacation_until >= today:
        return user.vacation_from, user.vacation_until
    return None


# ---------------------------------------------------------------- objectifs


def goal_progress(goal, *, now=None):
    """(fait, cible) : exercices résolus depuis la création, ou chronométrés cette semaine."""
    now = now or timezone.now()
    if goal.kind == Goal.Kind.TIMED_WEEKLY:
        week = Week.containing(now)
        done = TimedSession.objects.filter(
            user=goal.user, status=TimedSession.Status.SUBMITTED, submitted_at__gte=week.start, submitted_at__lt=week.end
        ).count()
        return done, goal.target
    solutions = Solution.objects.filter(author=goal.user, created_at__gte=goal.created_at).exclude(
        status=Solution.Status.DRAFT
    )
    if goal.topic_id:
        solutions = solutions.filter(exercise__topics=goal.topic_id)
    done = solutions.aggregate(count=Count("exercise", distinct=True))["count"]
    return done, goal.target


def create_goal(user, *, kind, target, deadline, title="", topic=None, today=None):
    today = today or timezone.localdate()
    if deadline <= today:
        raise RuleError("L'échéance d'un objectif est dans le futur.")
    if not 1 <= target <= 200:
        raise RuleError("Une cible entre 1 et 200.")
    if Goal.objects.filter(user=user, deadline__gte=today).count() >= 5:
        raise RuleError("Cinq objectifs en cours au plus : termine ou supprime-en un.")
    if not title.strip():
        title = (
            f"{target} exercice{'s' if target > 1 else ''} chronométré{'s' if target > 1 else ''} par semaine"
            if kind == Goal.Kind.TIMED_WEEKLY
            else f"{target} exercice{'s' if target > 1 else ''}" + (f" de {topic.name}" if topic else "")
        )
    return Goal.objects.create(user=user, kind=kind, target=target, deadline=deadline, title=title.strip(), topic=topic)

