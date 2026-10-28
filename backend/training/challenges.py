"""Défi du jour, un par niveau. Règles du document de conception :

- fenêtre de 24 h, 30 minutes, une seule tentative : abandonner la consomme ;
- gabarits paramétrés : chaque membre reçoit ses propres paramètres, partager sa
  réponse ne sert donc à rien (partager la méthode reste permis) ;
- barème 20 × m(d) : 60 % dès que SymPy reconnaît la réponse, 40 % quand la
  justification est validée par les pairs ; bonus de rapidité ×(1 + 0,25 × (1 − t/T))
  au plus, réduit de 10 % par indication ouverte ;
- le chrono ne s'arrête pas, sans pause ; collage externe désactivé et compté ;
- les solutions des autres sont visibles à la fermeture de la fenêtre.
"""

import math
import random
import re
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from catalog.models import Level
from config.errors import RuleError
from content.models import Exercise
from gamification.scoring import DIFFICULTY_MULTIPLIER
from notifications.models import Notification
from notifications.services import notify

from .answers import check_answer
from .models import EXTRA_TIME_FACTOR, Challenge, ChallengeTemplate, TimedSession

User = get_user_model()

MINUTES = 30
BASE_POINTS = 20
ANSWER_SHARE = 0.6
SPEED_BONUS = 0.25
HINT_PENALTY = 0.1
# Un gabarit ne revient pas dans le même niveau avant une semaine, s'il y a le choix.
REPEAT_AFTER_DAYS = 7
PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-z])\s*\}\}")
PARAMETER_RE = re.compile(r"^[a-z]$")
# Lettres réservées par la grammaire des réponses : e (Euler) et i (imaginaire).
RESERVED = {"e", "i"}


def check_template(template):
    """Liste des erreurs d'un gabarit : paramètres mal formés, placeholder inconnu,
    réponse illisible pour une valeur tirée."""
    errors = []
    parameters = template.parameters
    if not isinstance(parameters, dict) or not parameters:
        return ["Les paramètres sont un objet JSON : une lettre, et la liste de ses valeurs."]
    for name, values in parameters.items():
        if not PARAMETER_RE.match(name) or name in RESERVED:
            errors.append(f"« {name} » : un paramètre est une lettre minuscule, autre que e et i.")
        if not isinstance(values, list) or not values or not all(isinstance(v, int) for v in values):
            errors.append(f"« {name} » : donne une liste d'entiers.")
    for name in PLACEHOLDER_RE.findall(template.statement):
        if name not in parameters:
            errors.append(f"L'énoncé utilise {{{{{name}}}}}, qui n'est pas un paramètre.")
    if not errors:
        values = {name: options[0] for name, options in parameters.items()}
        if check_answer(expected_answer(template, values), expected_answer(template, values)) is not True:
            errors.append("La réponse ne se lit pas : elle doit s'écrire avec les paramètres, comme « sqrt(a)/b ».")
    return errors


def draw(template, rng):
    return {name: rng.choice(values) for name, values in template.parameters.items()}


def fill(template, values):
    """Énoncé avec les valeurs tirées."""
    return PLACEHOLDER_RE.sub(lambda match: str(values.get(match[1], match[0])), template.statement)


def expected_answer(template, values):
    """Réponse attendue, les paramètres remplacés par leurs valeurs : « sqrt(3)/(5) »."""
    return re.sub(
        r"\b([a-z])\b",
        lambda match: f"({values[match[1]]})" if match[1] in values else match[0],
        template.answer,
    )


def points_total(exercise):
    return BASE_POINTS * DIFFICULTY_MULTIPLIER[exercise.difficulty]


def speed_bonus(elapsed_s, limit_s, hints_opened):
    """×(1 + 0,25 × (1 − t/T)), la part de bonus réduite de 10 % par indication."""
    speed = max(0.0, 1 - elapsed_s / limit_s) if limit_s else 0.0
    return 1 + SPEED_BONUS * speed * max(0.0, 1 - HINT_PENALTY * hints_opened)


def score(session):
    """Fixe le bonus et les deux parts de points d'une session rendue."""
    total = points_total(session.exercise)
    session.bonus = speed_bonus(session.elapsed_s, session.limit_s, session.hints_opened)
    # Arrondi au demi supérieur, comme le reste du barème.
    answer = math.floor(total * ANSWER_SHARE * session.bonus + 0.5)
    session.answer_points = answer if session.answer_correct else 0
    session.justification_points = math.floor(total * (1 - ANSWER_SHARE) * session.bonus + 0.5)


def window(date):
    """De minuit à minuit, heure de Paris."""
    start = timezone.make_aware(datetime.combine(date, time.min))
    return start, timezone.make_aware(datetime.combine(date + timedelta(days=1), time.min))


def open_challenges(*, now=None, rng=None):
    """Ouvre le défi du jour de chaque niveau qui a un gabarit actif. Idempotent :
    la tâche horaire l'appelle, le premier passage après minuit ouvre les défis."""
    now = now or timezone.now()
    rng = rng or random.Random()
    today = timezone.localdate(now)
    opened = []
    templates = ChallengeTemplate.objects.filter(active=True, exercise__status=Exercise.Status.PUBLISHED)
    for level in Level.objects.filter(pk__in=templates.values("exercise__primary_level")):
        if Challenge.objects.filter(level=level, date=today).exists():
            continue
        candidates = list(templates.filter(exercise__primary_level=level).order_by("pk"))
        recent = set(
            Challenge.objects.filter(level=level, date__gte=today - timedelta(days=REPEAT_AFTER_DAYS)).values_list(
                "template_id", flat=True
            )
        )
        fresh = [template for template in candidates if template.pk not in recent] or candidates
        opens_at, closes_at = window(today)
        try:
            with transaction.atomic():
                challenge = Challenge.objects.create(
                    level=level, date=today, template=rng.choice(fresh), opens_at=opens_at, closes_at=closes_at
                )
        except IntegrityError:
            continue
        opened.append(challenge)
        for user in User.objects.filter(is_active=True, daily_challenge_notifications=True, declared_level=level):
            notify(
                user,
                Notification.Kind.CHALLENGE,
                f"Le défi du jour {level.code} est ouvert",
                "30 minutes, une seule tentative, jusqu'à minuit.",
                "/defi",
                now=now,
            )
    return opened


def open_today(now=None):
    now = now or timezone.now()
    return Challenge.objects.filter(opens_at__lte=now, closes_at__gt=now).select_related(
        "level", "template__exercise"
    )


@transaction.atomic
def start(user, challenge, *, rng=None, now=None):
    """Démarre le défi, ou reprend la tentative en cours : il n'y en a qu'une."""
    now = now or timezone.now()
    existing = TimedSession.objects.filter(user=user, challenge=challenge).first()
    if existing:
        return existing
    if not challenge.opens_at <= now < challenge.closes_at:
        raise RuleError("Ce défi est fermé.")
    exercise = challenge.template.exercise
    if TimedSession.objects.filter(
        user=user, exercise=exercise, status__in=[TimedSession.Status.RUNNING, TimedSession.Status.PAUSED]
    ).exists():
        raise RuleError("Termine d'abord ton entraînement en cours sur cet exercice.")
    try:
        with transaction.atomic():
            return TimedSession.objects.create(
                user=user,
                exercise=exercise,
                challenge=challenge,
                parameters=draw(challenge.template, rng or random.Random()),
                duration_s=MINUTES * 60,
                extra_time_factor=EXTRA_TIME_FACTOR if user.tiers_temps else 1.0,
                started_at=now,
                last_tick_at=now,
            )
    except IntegrityError:
        return TimedSession.objects.get(user=user, challenge=challenge)


def statement(session):
    """L'énoncé de la session : tiré pour le membre en défi, tel quel sinon."""
    if session.ranked:
        return fill(session.challenge.template, session.parameters)
    return session.exercise.statement


def expected(session):
    if session.ranked:
        return expected_answer(session.challenge.template, session.parameters)
    return session.exercise.final_answer


@transaction.atomic
def open_hint(session):
    """En défi, chaque indication s'ouvre à la demande et réduit le bonus de 10 %."""
    if not session.ranked or not session.open:
        raise RuleError("Rien à ouvrir ici.")
    if session.hints_opened < len(session.exercise.hints):
        session.hints_opened += 1
        session.save(update_fields=["hints_opened"])
    return session


def solutions_hidden_until(exercise, now=None):
    """Fin de la fenêtre d'un défi encore ouvert sur cet exercice, ou None."""
    challenge = (
        Challenge.objects.filter(template__exercise=exercise, closes_at__gt=now or timezone.now())
        .order_by("-closes_at")
        .first()
    )
    return challenge.closes_at if challenge else None
