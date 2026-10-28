"""API des contenus : lecture publique, puis écriture réservée aux contributeurs
(compte actif, email vérifié)."""

import random
from datetime import datetime
from typing import Literal

from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle
from pydantic import Field

from accounts.permissions import contributor
from catalog.models import Level, Topic
from duplicates.models import DuplicatePair
from duplicates.services import (
    DuplicateSuspected,
    compute_prints,
    find_similar,
    publish_checked,
    variants_of,
)

from .feed import FEED_LABELS, build_feed, compute_scores, record_impressions
from .latex import forbidden_commands
from .models import TEXT_MAX_LENGTH, Exercise, Review, Solution, Vote
from .services import cast_vote, publish_solution, submit_review

router = Router(tags=["contenus"])


# ---------------------------------------------------------------- lecture


class LevelOut(Schema):
    code: str
    name: str
    track: str
    year: int


class TopicOut(Schema):
    name: str
    slug: str


class ExerciseSummary(Schema):
    id: int
    title: str
    difficulty: int
    primary_level: str
    levels: list[str]
    topics: list[str]
    validated_solutions: int
    votes: int
    published_at: datetime

    @staticmethod
    def resolve_primary_level(obj):
        return obj.primary_level.code

    @staticmethod
    def resolve_votes(obj):
        return obj.vote_count

    @staticmethod
    def resolve_levels(obj):
        return [level.code for level in obj.levels.all()]

    @staticmethod
    def resolve_topics(obj):
        return [topic.name for topic in obj.topics.all()]


class SolutionOut(Schema):
    id: int
    author: str | None
    body: str
    ai_usage: str
    votes: int
    validated_at: datetime | None

    @staticmethod
    def resolve_author(obj):
        return obj.author.username if obj.author else None

    @staticmethod
    def resolve_votes(obj):
        return obj.vote_count


class ExerciseLinkOut(Schema):
    id: int
    title: str


class ExerciseDetail(ExerciseSummary):
    statement: str
    hints: list[str]
    author: str | None
    source_type: str
    source_reference: str
    license: str
    merged_into: int | None
    variants: list[ExerciseLinkOut]
    solutions: list[SolutionOut]

    @staticmethod
    def resolve_author(obj):
        return obj.author.username if obj.author else None

    @staticmethod
    def resolve_merged_into(obj):
        return obj.merged_into_id

    @staticmethod
    def resolve_variants(obj):
        return variants_of(obj)

    @staticmethod
    def resolve_solutions(obj):
        return (
            obj.solutions.filter(status=Solution.Status.VALIDATED)
            .select_related("author")
            .annotate(vote_count=Count("votes"))
        )


def published_exercises(statuses=(Exercise.Status.PUBLISHED,)):
    # distinct : le filtre par niveau ajoute une jointure qui dupliquerait les lignes.
    return (
        Exercise.objects.filter(status__in=statuses)
        .select_related("primary_level", "author")
        .prefetch_related("levels", "topics")
        .annotate(
            validated_solutions=Count(
                "solutions",
                filter=Q(solutions__status=Solution.Status.VALIDATED),
                distinct=True,
            ),
            vote_count=Count("votes", distinct=True),
        )
    )


@router.get("/levels", response=list[LevelOut])
def list_levels(request):
    return Level.objects.all()


@router.get("/topics", response=list[TopicOut])
def list_topics(request):
    return Topic.objects.all()


class FeedItemOut(ExerciseSummary):
    """Exercice du fil d'accueil, avec la raison de sa présence."""

    reason: Literal["tendance", "a_resoudre", "exploration"]
    reason_label: str


def at_level(exercises, level):
    """Exercices du niveau, principal ou secondaire ; tous si `level` est vide."""
    if not level:
        return exercises
    return exercises.filter(Q(primary_level__code=level) | Q(levels__code=level)).distinct()


@router.get("/exercises", response=list[ExerciseSummary])
def list_exercises(
    request, level: str | None = None, sort: Literal["recent", "popular", "unsolved"] = "recent"
):
    """Exercices publiés : les plus récents, les plus populaires (score P), ou ceux
    qui attendent encore une solution validée."""
    exercises = at_level(published_exercises(), level)
    if sort == "unsolved":
        return exercises.filter(validated_solutions=0)
    if sort == "popular":
        exercises = list(exercises)
        scores = compute_scores(exercises)
        return sorted(exercises, key=lambda e: (-scores[e.pk].popular, -e.published_at.timestamp()))
    return exercises


@router.get("/feed", response=list[FeedItemOut])
def feed(request, level: str | None = None):
    """Fil d'accueil d'un niveau, ou de tous : 60 % Tendances, 25 % À résoudre,
    15 % exploration, sur une seule page. Chaque exercice dit pourquoi il est là."""
    if level and not Level.objects.filter(code=level).exists():
        raise HttpError(404, "Niveau inconnu.")
    now = timezone.now()
    visitor = request.user.pk if request.user.is_authenticated else "anonyme"
    # Le tirage de l'exploration ne change pas d'un rechargement à l'autre dans la journée.
    rng = random.Random(f"{timezone.localdate(now)}:{level}:{visitor}")
    items = build_feed(at_level(published_exercises(), level), now=now, rng=rng)
    record_impressions(items)
    for exercise, source in items:
        exercise.reason = source
        exercise.reason_label = FEED_LABELS[source]
    return [exercise for exercise, _ in items]


@router.get("/exercises/{int:exercise_id}", response=ExerciseDetail)
def get_exercise(request, exercise_id: int):
    """Un exercice fusionné reste lisible : `merged_into` donne l'adresse canonique."""
    return get_object_or_404(
        published_exercises((Exercise.Status.PUBLISHED, Exercise.Status.MERGED)), pk=exercise_id
    )


# ---------------------------------------------------------------- écriture


class ExerciseIn(Schema):
    title: str = Field(min_length=3, max_length=200)
    statement: str = Field(min_length=10, max_length=TEXT_MAX_LENGTH)
    hints: list[str] = Field(default_factory=list, max_length=5)
    final_answer: str = Field(default="", max_length=500)
    difficulty: int = Field(ge=1, le=5)
    primary_level: str
    levels: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list, description="Slugs des chapitres.")
    source_type: Literal["personnel", "inspire", "reproduit"] = "personnel"
    source_reference: str = Field(default="", max_length=300)


class DraftOut(Schema):
    id: int
    status: str


class StatementIn(Schema):
    statement: str = Field(max_length=TEXT_MAX_LENGTH)
    exercise_id: int | None = Field(None, description="Brouillon en cours d'édition, à exclure.")


class SimilarExerciseOut(Schema):
    """Exercice publié proche d'un énoncé, avec la bande de similarité."""

    id: int
    title: str
    statement: str
    primary_level: str
    validated_solutions: int
    band: str
    band_label: str
    score: float | None


class PublishIn(Schema):
    """Réponse de l'auteur à l'écran « Cet exercice existe peut-être déjà »."""

    choice: Literal["", "variante", "different"] = ""
    target_id: int | None = None
    note: str = Field(default="", max_length=300)


class DuplicateCheckOut(Schema):
    detail: str
    candidates: list[SimilarExerciseOut]


class SolutionIn(Schema):
    body: str = Field(min_length=20, max_length=TEXT_MAX_LENGTH)
    ai_usage: Literal["aucune", "relecture", "aide_idee", "generee"] = "aucune"


class MySolutionOut(Schema):
    id: int
    body: str
    ai_usage: str
    status: str
    published_at: datetime | None
    validated_at: datetime | None
    feedback: list[str]

    @staticmethod
    def resolve_feedback(obj):
        # Les retours des relecteurs ne sont visibles qu'une fois la relecture close.
        if obj.status not in (Solution.Status.VALIDATED, Solution.Status.NEEDS_WORK):
            return []
        return [
            review.feedback
            for review in obj.reviews.exclude(submitted_at=None)
            if review.feedback
        ]


class VoteOut(Schema):
    weight: float


class ReviewTaskOut(Schema):
    """Relecture à faire. L'auteur de la solution n'est pas montré : relecture anonyme."""

    id: int
    assigned_at: datetime
    exercise_id: int
    exercise_title: str
    exercise_statement: str
    primary_level: str
    solution_body: str
    ai_usage: str

    @staticmethod
    def resolve_exercise_id(obj):
        return obj.solution.exercise_id

    @staticmethod
    def resolve_exercise_title(obj):
        return obj.solution.exercise.title

    @staticmethod
    def resolve_exercise_statement(obj):
        return obj.solution.exercise.statement

    @staticmethod
    def resolve_primary_level(obj):
        return obj.solution.exercise.primary_level.code

    @staticmethod
    def resolve_solution_body(obj):
        return obj.solution.body

    @staticmethod
    def resolve_ai_usage(obj):
        return obj.solution.ai_usage


class ReviewIn(Schema):
    verdict: Literal["correcte", "lacunes", "incorrecte"]
    feedback: str = Field(default="", max_length=5000)


class ReviewResult(Schema):
    solution_status: str


def reject_forbidden_latex(fields):
    """`fields` : couples (libellé, texte). Refuse en 422 les commandes interdites."""
    for label, text in fields:
        found = forbidden_commands(text)
        if found:
            raise HttpError(
                422, f"Commandes LaTeX non autorisées dans {label} : {', '.join(found)}."
            )


def _draft_fields(payload):
    """Valide un brouillon. Renvoie ses champs, ses niveaux et ses chapitres."""
    hints = [hint.strip() for hint in payload.hints if hint.strip()]
    reject_forbidden_latex(
        [
            ("l'énoncé", payload.statement),
            ("les indications", "\n".join(hints)),
            ("la réponse finale", payload.final_answer),
        ]
    )
    codes = {payload.primary_level, *payload.levels}
    levels = {level.code: level for level in Level.objects.filter(code__in=codes)}
    if levels.keys() != codes:
        raise HttpError(422, f"Niveau inconnu : {', '.join(sorted(codes - levels.keys()))}.")
    slugs = set(payload.topics)
    topics = list(Topic.objects.filter(slug__in=slugs))
    if len(topics) != len(slugs):
        raise HttpError(422, "Chapitre inconnu.")
    source_reference = payload.source_reference.strip()
    if payload.source_type != Exercise.SourceType.PERSONAL and not source_reference:
        raise HttpError(422, "Indique la source de l'exercice.")

    fields = {
        "title": payload.title.strip(),
        "statement": payload.statement.strip(),
        "hints": hints,
        "final_answer": payload.final_answer.strip(),
        "difficulty_declared": payload.difficulty,
        "primary_level": levels[payload.primary_level],
        "source_type": payload.source_type,
        "source_reference": source_reference,
    }
    return fields, list(levels.values()), topics


@router.post("/exercises", response={201: DraftOut}, auth=django_auth)
def create_exercise(request, payload: ExerciseIn):
    """Crée un brouillon. La publication est une étape à part, qui vérifie les doublons."""
    user = contributor(request)
    fields, levels, topics = _draft_fields(payload)
    exercise = Exercise.objects.create(author=user, **fields)
    exercise.levels.set(levels)
    exercise.topics.set(topics)
    return 201, exercise


@router.put("/exercises/{int:exercise_id}", response=DraftOut, auth=django_auth)
def update_draft(request, exercise_id: int, payload: ExerciseIn):
    """Modifie un brouillon, par exemple après l'écran des doublons."""
    user = contributor(request)
    exercise = get_object_or_404(
        Exercise, pk=exercise_id, author=user, status=Exercise.Status.DRAFT
    )
    fields, levels, topics = _draft_fields(payload)
    for name, value in fields.items():
        setattr(exercise, name, value)
    exercise.save()
    exercise.levels.set(levels)
    exercise.topics.set(topics)
    return exercise


def _similar_out(matches):
    exercises = published_exercises().in_bulk([match.exercise.pk for match in matches])
    return [
        {
            "id": exercise.pk,
            "title": exercise.title,
            "statement": exercise.statement,
            "primary_level": exercise.primary_level.code,
            "validated_solutions": exercise.validated_solutions,
            "band": match.band,
            "band_label": DuplicatePair.Band(match.band).label,
            "score": match.score,
        }
        for match in matches
        if (exercise := exercises.get(match.exercise.pk))
    ]


@router.post(
    "/exercises/similar",
    response=list[SimilarExerciseOut],
    auth=django_auth,
    throttle=[AuthRateThrottle("30/m")],
)
def similar_exercises(request, payload: StatementIn):
    """Exercices publiés proches d'un énoncé en cours de rédaction."""
    user = contributor(request)
    draft = None
    if payload.exercise_id is not None:
        draft = Exercise.objects.filter(pk=payload.exercise_id, author=user).first()
    return _similar_out(find_similar(compute_prints(payload.statement), exercise=draft))


@router.post(
    "/exercises/{exercise_id}/publish",
    response={200: ExerciseDetail, 409: DuplicateCheckOut},
    auth=django_auth,
)
def publish(request, exercise_id: int, payload: PublishIn):
    """Publie un brouillon. Si un exercice publié est proche, répond 409 avec les
    candidats : l'auteur dit alors s'il s'agit d'une variante ou d'un exercice
    différent, et republie avec son choix. Rien n'est bloqué définitivement."""
    user = contributor(request)
    exercise = get_object_or_404(Exercise, pk=exercise_id, author=user)
    note = payload.note.strip()
    if payload.choice == DuplicatePair.AuthorChoice.DIFFERENT and not note:
        raise HttpError(422, "Dis en une phrase ce qui change par rapport à l'exercice existant.")
    try:
        publish_checked(exercise, choice=payload.choice, target_id=payload.target_id, note=note)
    except DuplicateSuspected as suspected:
        return 409, {"detail": str(suspected), "candidates": _similar_out(suspected.matches)}
    return 200, get_object_or_404(published_exercises(), pk=exercise_id)


@router.post(
    "/exercises/{exercise_id}/solutions",
    response={201: MySolutionOut},
    auth=django_auth,
)
def propose_solution(request, exercise_id: int, payload: SolutionIn):
    user = contributor(request)
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    if Solution.objects.filter(
        exercise=exercise,
        author=user,
        status__in=[Solution.Status.UNDER_REVIEW, Solution.Status.CONTESTED],
    ).exists():
        raise HttpError(409, "Tu as déjà une solution en cours d'évaluation sur cet exercice.")
    reject_forbidden_latex([("la solution", payload.body)])
    solution = Solution.objects.create(
        exercise=exercise, author=user, body=payload.body.strip(), ai_usage=payload.ai_usage
    )
    publish_solution(solution)
    return 201, solution


@router.get(
    "/exercises/{exercise_id}/my-solutions",
    response=list[MySolutionOut],
    auth=django_auth,
)
def my_solutions(request, exercise_id: int):
    return (
        Solution.objects.filter(exercise_id=exercise_id, author=request.auth)
        .exclude(status=Solution.Status.DRAFT)
        .prefetch_related("reviews")
        .order_by("-published_at")
    )


def _vote(user, **target):
    if Vote.objects.filter(voter=user, **target).exists():
        raise HttpError(409, "Tu as déjà voté.")
    try:
        return cast_vote(user, **target)
    except IntegrityError:
        raise HttpError(409, "Tu as déjà voté.")


@router.post("/exercises/{exercise_id}/vote", response={201: VoteOut}, auth=django_auth)
def vote_for_exercise(request, exercise_id: int):
    user = contributor(request)
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    return 201, _vote(user, exercise=exercise)


@router.post("/solutions/{solution_id}/vote", response={201: VoteOut}, auth=django_auth)
def vote_for_solution(request, solution_id: int):
    user = contributor(request)
    solution = get_object_or_404(
        Solution.objects.select_related("exercise"),
        pk=solution_id,
        status=Solution.Status.VALIDATED,
    )
    return 201, _vote(user, solution=solution)


@router.get("/reviews", response=list[ReviewTaskOut], auth=django_auth)
def pending_reviews(request):
    return (
        Review.objects.filter(
            reviewer=request.auth,
            submitted_at=None,
            solution__status=Solution.Status.UNDER_REVIEW,
        )
        .select_related("solution__exercise__primary_level")
        .order_by("assigned_at")
    )


@router.post("/reviews/{review_id}", response=ReviewResult, auth=django_auth)
def review_solution(request, review_id: int, payload: ReviewIn):
    user = contributor(request)
    review = get_object_or_404(
        Review.objects.select_related("solution__exercise", "reviewer"),
        pk=review_id,
        reviewer=user,
    )
    if review.solution.status != Solution.Status.UNDER_REVIEW:
        raise HttpError(409, "Cette solution n'est plus en relecture.")
    feedback = payload.feedback.strip()
    if payload.verdict != Review.Verdict.CORRECT and not feedback:
        raise HttpError(
            422,
            "Explique en quelques mots ce qui manque ou ce qui est faux : "
            "c'est ce qui aide l'auteur à progresser.",
        )
    status = submit_review(review, payload.verdict, feedback=feedback)
    return {"solution_status": status}
