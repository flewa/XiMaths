"""Question de compréhension, la mesure centrale de l'anti-triche (document, §6).

- Score d'intégrité, entre 0 et 1. Les copies sont manuscrites et photographiées : il
  n'y a plus de texte à comparer ni de collage possible. Reste un signal mesurable, le
  temps : un défi rendu bien plus vite que les autres.
- Seulement pour une solution classée (défi) ou à fort enjeu (plus de 30 points).
  En dessous de 0,4 rien ; jusqu'à 0,7 une relecture supplémentaire ; au-delà, une
  question de compréhension.
- La question arrive sous 72 h : rédigée par Claude si un LLM est configuré, par un
  modérateur sinon. Le membre a ensuite 72 h pour l'ouvrir, et 5 minutes pour répondre.
- Un relecteur de niveau 3 ou un modérateur évalue ; le LLM peut préparer l'évaluation.
  Réussie : les points sont accordés, et aucune question pendant 30 jours. Sans réponse
  ou insuffisante : la solution reste publiée, sans ses points de classement.
- Une question tous les 14 jours au plus, sauf dossier de modération ouvert.
"""

from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from config import llm
from content import photos
from content.models import Solution
from gamification.scoring import validated_solution_points
from notifications.models import Notification
from notifications.services import notify
from training.models import TimedSession

from .models import ComprehensionQuestion, IntegritySignal, Report

Status = ComprehensionQuestion.Status

EXTRA_REVIEW_SCORE = 0.4
QUESTION_SCORE = 0.7
HIGH_STAKES_POINTS = 30
WRITE_WITHIN = timedelta(hours=72)
OPEN_WITHIN = timedelta(hours=72)
ANSWER_WITHIN = timedelta(minutes=5)
GRACE = timedelta(seconds=30)
COOLDOWN = timedelta(days=14)
EXEMPTION = timedelta(days=30)
# Points retenus tant que la question n'est pas réussie (ou abandonnée faute d'avoir été posée).
HOLDING = {Status.TO_WRITE, Status.SENT, Status.OPENED, Status.ANSWERED, Status.FAILED, Status.EXPIRED}

EXTRA_REVIEW = "relecture_supplementaire"
QUESTION = "question"


def integrity_score(solution, session=None):
    """0 sans session chronométrée. Sinon, de plus en plus proche de 1 quand la copie est
    rendue en moins de la moitié du temps médian des autres sur cet exercice."""
    if session is None:
        return 0.0
    times = sorted(
        TimedSession.objects.filter(exercise=session.exercise, status=TimedSession.Status.SUBMITTED)
        .exclude(pk=session.pk)
        .values_list("elapsed_s", flat=True)
    )
    if not times:
        return 0.0
    median = times[len(times) // 2]
    return max(0.0, 1 - session.elapsed_s / (0.5 * median)) if median else 0.0


def high_stakes(solution, session):
    if session is not None and session.challenge_id:
        return True
    return validated_solution_points(solution.exercise.difficulty, solution.ai_usage) > HIGH_STAKES_POINTS


def _may_ask(user, now):
    """Plafond d'une question tous les 14 jours, sauf dossier de modération ouvert ;
    exemption de 30 jours après une question réussie."""
    questions = ComprehensionQuestion.objects.filter(user=user)
    if questions.filter(status=Status.PASSED, evaluated_at__gte=now - EXEMPTION).exists():
        return False
    open_case = (
        IntegritySignal.objects.filter(user=user, status=IntegritySignal.Status.OPEN).exists()
        or Report.objects.filter(status=Report.Status.OPEN)
        .filter(Q(exercise__author=user) | Q(solution__author=user))
        .exists()
    )
    return open_case or not questions.filter(created_at__gte=now - COOLDOWN).exists()


def assess(solution, *, now=None):
    """Score d'intégrité d'une solution qui vient d'être publiée. Renvoie EXTRA_REVIEW
    (à l'appelant d'ajouter un relecteur), QUESTION (question créée) ou None."""
    if solution.author is None or solution.status != Solution.Status.UNDER_REVIEW:
        return None
    session = TimedSession.objects.filter(solution=solution).first()
    if not high_stakes(solution, session):
        return None
    now = now or timezone.now()
    score = integrity_score(solution, session)
    if score < EXTRA_REVIEW_SCORE:
        return None
    if score < QUESTION_SCORE or not _may_ask(solution.author, now):
        return EXTRA_REVIEW
    try:
        with transaction.atomic():
            ComprehensionQuestion.objects.create(solution=solution, user=solution.author, integrity_score=score)
    except IntegrityError:
        return None
    return QUESTION


def points_on_hold(solution):
    """Les points de classement de cette solution attendent-ils une question ?"""
    return ComprehensionQuestion.objects.filter(solution=solution, status__in=HOLDING).exists()


def send(question, *, now=None):
    """La question est rédigée : le membre est prévenu, il a 72 h pour l'ouvrir."""
    now = now or timezone.now()
    question.status = Status.SENT
    question.sent_at = now
    question.save(update_fields=["status", "sent_at", "question", "expected_points", "generated_by_llm"])
    notify(
        question.user,
        Notification.Kind.COMPREHENSION_QUESTION,
        "Une question sur ta solution",
        f"Exercice « {question.solution.exercise.title} ». Une question courte sur ta propre solution, "
        "à ouvrir sous 72 heures ; tu auras ensuite 5 minutes pour répondre. Ce n'est pas une "
        "accusation : en cas de réussite, les points de ta solution sont accordés.",
        "/questions",
        now=now,
    )
    return question


# ---------------------------------------------------------------- avec un LLM

QUESTION_SYSTEM = (
    "Tu aides une plateforme d'exercices de mathématiques du supérieur à vérifier qu'un "
    "étudiant comprend sa propre solution. Rédige une seule question courte, en français, "
    "en tutoyant, sur un choix précis de cette solution : pourquoi une étape est permise, "
    "à quoi sert une hypothèse, ou ce que devient le résultat si l'on change une donnée. "
    "Un étudiant qui a compris sa solution doit pouvoir y répondre en cinq minutes, sans "
    "document. Ton neutre, jamais accusateur ; ne mentionne ni triche ni IA. Donne aussi, "
    "pour l'évaluateur, deux à quatre éléments qu'une bonne réponse contient."
)
QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        "expected_points": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["question", "expected_points"],
    "additionalProperties": False,
}
ASSESSMENT_SYSTEM = (
    "Tu prépares l'évaluation d'une réponse à une question de compréhension, posée à un "
    "étudiant sur sa propre solution d'un exercice de mathématiques. Un humain décidera : "
    "ton avis l'aide seulement. Juge si la réponse montre que l'étudiant comprend le "
    "point soulevé, sans exiger de rédaction parfaite : il avait cinq minutes. Réponds "
    "« convaincante », « partielle » ou « insuffisante », avec un motif de deux phrases au plus."
)
ASSESSMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "assessment": {"type": "string", "enum": [choice.value for choice in ComprehensionQuestion.Assessment]},
        "rationale": {"type": "string"},
    },
    "required": ["assessment", "rationale"],
    "additionalProperties": False,
}


def _statement(solution):
    return solution.variant_statement or solution.exercise.statement


def _solution_blocks(solution, before, after=""):
    """La solution pour Claude : son texte, et les photos de la copie s'il y en a."""
    pictures = photos.llm_blocks(solution)
    if not pictures:
        return f"{before}{solution.body}{after}"
    note = f"{solution.body}\n\n" if solution.body.strip() else ""
    return [
        {"type": "text", "text": f"{before}{note}(Copie manuscrite de l'étudiant, en {len(pictures)} photo(s) :)"},
        *pictures,
        {"type": "text", "text": after or "(Fin de la copie.)"},
    ]


def write_with_llm(question):
    """Rédige la question avec Claude. Renvoie True si elle est prête."""
    solution = question.solution
    answer = llm.ask_json(
        llm.COMPREHENSION_MODEL,
        system=QUESTION_SYSTEM,
        prompt=_solution_blocks(solution, f"Énoncé :\n\n{_statement(solution)}\n\n---\n\nSolution de l'étudiant :\n\n"),
        schema=QUESTION_SCHEMA,
        effort="medium",
    )
    text = (answer or {}).get("question", "").strip()
    if not text:
        return False
    question.question = text
    question.expected_points = [point.strip() for point in answer.get("expected_points", []) if point.strip()][:6]
    question.generated_by_llm = True
    return True


def preassess_with_llm(question):
    solution = question.solution
    expected = "\n".join(f"- {point}" for point in question.expected_points) or "(non précisés)"
    answer = llm.ask_json(
        llm.COMPREHENSION_MODEL,
        system=ASSESSMENT_SYSTEM,
        prompt=_solution_blocks(
            solution,
            f"Énoncé :\n\n{_statement(solution)}\n\n---\n\nSolution de l'étudiant :\n\n",
            f"\n\n---\n\nQuestion posée : {question.question}\n\nÉléments attendus :\n{expected}\n\n"
            f"---\n\nRéponse de l'étudiant, écrite en cinq minutes :\n\n{question.answer}",
        ),
        schema=ASSESSMENT_SCHEMA,
        effort="high",
    )
    if answer and answer.get("assessment") in ComprehensionQuestion.Assessment.values:
        question.llm_assessment = answer["assessment"]
        question.llm_rationale = answer.get("rationale", "").strip()
        question.save(update_fields=["llm_assessment", "llm_rationale"])
