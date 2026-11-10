"""API des contenus : lecture publique, puis écriture réservée aux contributeurs
(compte actif, email vérifié)."""

import random
from datetime import datetime, timedelta
from typing import Literal

from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import File, Router, Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja.security import django_auth
from pydantic import Field

from accounts.links import linked_ids
from accounts.permissions import contributor, is_moderator
from accounts.profile import is_editorial
from accounts.schemas import MemberRefOut
from catalog.models import Level, Topic
from config.errors import RuleError
from config.throttles import AnonRouteThrottle, AuthRouteThrottle
from duplicates.models import DuplicatePair
from duplicates.services import (
    DuplicateSuspected,
    compute_prints,
    find_similar,
    publish_checked,
    variants_of,
)

from . import photos
from .feed import FEED_LABELS, build_feed, compute_scores, record_impressions
from .latex import forbidden_commands, plain_math, title_problems
from .models import TEXT_MAX_LENGTH, Exercise, ExerciseRead, Review, Solution, SolutionPhoto, Vote
from .services import (
    can_review,
    cast_vote,
    publish_solution,
    review_progress,
    revise_solution,
    submit_review,
    volunteer_review,
)

# Un exercice reste « Nouveau » une semaine après sa publication.
NEW_FOR = timedelta(days=7)

router = Router(tags=["contenus"])


# ---------------------------------------------------------------- lecture


class LevelOut(Schema):
    code: str
    name: str
    track: str
    year: int


class TopicOut(Schema):
    """Chapitre (parent vide) ou notion, rangée sous son chapitre (slug du parent)."""

    name: str
    slug: str
    parent: str | None
    # Exercices publiés de ce chapitre ou de cette notion.
    exercises: int

    @staticmethod
    def resolve_parent(obj):
        return obj.parent.slug if obj.parent else None

    @staticmethod
    def resolve_exercises(obj):
        return obj.published_count


class ExerciseSummary(Schema):
    id: int
    # Titre, formules entre $…$ ; et le même en texte, pour l'onglet et les moteurs.
    title: str
    title_text: str
    difficulty: int
    primary_level: str
    levels: list[str]
    # Chapitres, puis notions (sous-chapitres) : noms.
    topics: list[str]
    notions: list[str]
    validated_solutions: int
    # Solutions envoyées (en relecture, validées ou à reprendre) : le compteur affiché. Les
    # solutions elles-mêmes restent privées.
    submitted_solutions: int
    votes: int
    published_at: datetime
    # Publié depuis moins de NEW_FOR : le site l'affiche « Nouveau ».
    is_new: bool
    # Auteur, quand c'est un membre : vide pour les exercices de la rédaction.
    author_profile: MemberRefOut | None

    @staticmethod
    def resolve_author_profile(obj):
        return obj.author if obj.author and not is_editorial(obj.author) else None

    @staticmethod
    def resolve_primary_level(obj):
        return obj.primary_level.code

    @staticmethod
    def resolve_title_text(obj):
        return plain_math(obj.title)

    @staticmethod
    def resolve_is_new(obj):
        return obj.published_at is not None and obj.published_at > timezone.now() - NEW_FOR

    @staticmethod
    def resolve_votes(obj):
        return obj.vote_count

    @staticmethod
    def resolve_levels(obj):
        return [level.code for level in obj.levels.all()]

    @staticmethod
    def resolve_topics(obj):
        return [topic.name for topic in obj.topics.all() if topic.parent_id is None]

    @staticmethod
    def resolve_notions(obj):
        return [topic.name for topic in obj.topics.all() if topic.parent_id is not None]


class PhotoOut(Schema):
    """Photo d'une page de copie : l'adresse vérifie qui la demande."""

    id: int
    url: str
    width: int
    height: int


class ExerciseLinkOut(Schema):
    id: int
    title: str


class ExerciseStatsOut(Schema):
    """Qui a lu l'exercice, qui s'y est essayé, qui l'a réussi : des personnes, pas des copies."""

    readers: int
    senders: int
    solvers: int


def exercise_stats(exercise):
    sent = exercise.solutions.exclude(status__in=[Solution.Status.DRAFT, Solution.Status.HIDDEN]).exclude(author=None)
    senders = set(sent.values_list("author_id", flat=True))
    solvers = set(sent.filter(status=Solution.Status.VALIDATED).values_list("author_id", flat=True))
    # Qui a envoyé une copie a lu l'énoncé, même avant que les lectures soient comptées.
    members = set(exercise.reads.values_list("user_id", flat=True)) | senders
    return {"readers": exercise.visitor_reads + len(members), "senders": len(senders), "solvers": len(solvers)}


class ExerciseDetail(ExerciseSummary):
    statement: str
    hints: list[str]
    author: str | None
    stats: ExerciseStatsOut
    source_type: str
    source_reference: str
    license: str
    merged_into: int | None
    variants: list[ExerciseLinkOut]

    @staticmethod
    def resolve_author(obj):
        return obj.author.username if obj.author else None

    @staticmethod
    def resolve_stats(obj):
        return exercise_stats(obj)

    @staticmethod
    def resolve_merged_into(obj):
        return obj.merged_into_id

    @staticmethod
    def resolve_variants(obj):
        return variants_of(obj)



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
            submitted_solutions=Count(
                "solutions",
                filter=Q(solutions__published_at__isnull=False)
                & ~Q(solutions__status__in=[Solution.Status.DRAFT, Solution.Status.HIDDEN]),
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
    return Topic.objects.select_related("parent").annotate(
        published_count=Count("exercises", filter=Q(exercises__status=Exercise.Status.PUBLISHED), distinct=True)
    )


class FeedItemOut(ExerciseSummary):
    """Exercice du fil d'accueil, avec la raison de sa présence."""

    reason: Literal["tendance", "a_resoudre", "exploration"]
    reason_label: str


def at_level(exercises, level):
    """Exercices du niveau, principal ou secondaire ; tous si `level` est vide."""
    if not level:
        return exercises
    return exercises.filter(Q(primary_level__code=level) | Q(levels__code=level)).distinct()


# Au-delà, une recherche n'apporte rien de plus qu'une poignée de mots.
SEARCH_MAX_LENGTH = 100


def matching(exercises, text):
    """Exercices dont le titre, l'énoncé ou un chapitre (ou une notion) contient chacun des
    mots de `text`, sans tenir compte de la casse."""
    for word in text[:SEARCH_MAX_LENGTH].split():
        exercises = exercises.filter(
            Q(title__icontains=word) | Q(statement__icontains=word) | Q(topics__name__icontains=word)
        )
    return exercises.distinct()


@router.get("/exercises", response=list[ExerciseSummary])
def list_exercises(
    request,
    level: str | None = None,
    topic: str | None = None,
    sort: Literal["recent", "popular", "trending", "unsolved"] = "recent",
    q: str | None = None,
):
    """Exercices publiés : les plus récents, les plus populaires (score P), ceux dont on parle
    en ce moment (score T), ou ceux auxquels personne n'a encore envoyé de solution. `topic` : slug
    d'un chapitre ou d'une notion ; `q` : mots cherchés dans le titre, l'énoncé et les chapitres."""
    exercises = at_level(published_exercises(), level)
    if topic:
        exercises = exercises.filter(topics__slug=topic).distinct()
    if q and q.strip():
        exercises = matching(exercises, q)
    if sort == "unsolved":
        return exercises.filter(submitted_solutions=0)
    if sort in ("popular", "trending"):
        exercises = list(exercises)
        scores = compute_scores(exercises)
        return sorted(exercises, key=lambda e: (-getattr(scores[e.pk], sort), -e.published_at.timestamp()))
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


class SitemapEntry(Schema):
    id: int
    updated_at: datetime


@router.get("/sitemap", response=list[SitemapEntry])
def sitemap(request):
    """Exercices publiés, pour le plan du site : les fusionnés renvoient à leur canonique."""
    return Exercise.objects.filter(status=Exercise.Status.PUBLISHED).only("pk", "updated_at").order_by("pk")


@router.get("/exercises/{int:exercise_id}", response=ExerciseDetail)
def get_exercise(request, exercise_id: int):
    """Un exercice fusionné reste lisible : `merged_into` donne l'adresse canonique."""
    return get_object_or_404(
        published_exercises((Exercise.Status.PUBLISHED, Exercise.Status.MERGED)), pk=exercise_id
    )


@router.post(
    "/exercises/{int:exercise_id}/read",
    response={204: None},
    throttle=[AnonRouteThrottle("lecture", "300/h")],
)
def read_exercise(request, exercise_id: int):
    """La page de l'exercice a été ouverte. Un membre compte une fois par exercice, son
    auteur jamais ; un visiteur compte une fois par navigateur (c'est le site qui s'en
    souvient). Aucune adresse ni identifiant de visiteur n'est gardé."""
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    user = request.user
    if not user.is_authenticated:
        Exercise.objects.filter(pk=exercise.pk).update(visitor_reads=F("visitor_reads") + 1)
    elif exercise.author_id != user.pk:
        ExerciseRead.objects.get_or_create(exercise=exercise, user=user)
    return 204, None


# ---------------------------------------------------------------- écriture


class ExerciseIn(Schema):
    title: str = Field(min_length=3, max_length=200)
    statement: str = Field(min_length=10, max_length=TEXT_MAX_LENGTH)
    hints: list[str] = Field(default_factory=list, max_length=5)
    final_answer: str = Field(default="", max_length=500)
    difficulty: int = Field(ge=1, le=5)
    primary_level: str
    levels: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list, description="Slugs des chapitres et des notions.")
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
    """Une solution est la copie manuscrite, en photos : rien n'est tapé."""

    ai_usage: Literal["aucune", "relecture", "aide_idee", "generee"] = "aucune"
    # Jeton de l'envoi de photos (QR code).
    photo_upload: str = Field(min_length=1, max_length=64)


NO_PHOTOS = "Joins les photos de ta copie : une solution s'envoie en photos."


def pending_upload(user, exercise, token):
    """L'envoi de photos `token` de l'auteur, avec au moins une photo, ou une erreur 422."""
    try:
        upload = photos.upload_for(user, exercise, token)
    except RuleError as error:
        raise HttpError(422, str(error))
    if not photos.pending(upload).exists():
        raise HttpError(422, NO_PHOTOS)
    return upload


class AuthorReviewOut(Schema):
    verdict: str
    verdict_label: str
    comment: str
    submitted_at: datetime

    @staticmethod
    def resolve_verdict_label(obj):
        return obj.get_verdict_display()

    @staticmethod
    def resolve_comment(obj):
        return obj.feedback


class MySolutionOut(Schema):
    id: int
    body: str
    photos: list[PhotoOut]
    ai_usage: str
    status: str
    published_at: datetime | None
    validated_at: datetime | None
    # Relectures rendues du tour en cours, anonymes : verdict et commentaire, lisibles par
    # l'auteur dès qu'elles arrivent ; et le nombre de relectures attendues.
    reviews: list[AuthorReviewOut]
    reviews_expected: int

    @staticmethod
    def resolve_photos(obj):
        return photos.described(obj)

    @staticmethod
    def resolve_reviews(obj):
        return obj.reviews.filter(round=obj.review_round).exclude(submitted_at=None).order_by("submitted_at")

    @staticmethod
    def resolve_reviews_expected(obj):
        if obj.status == Solution.Status.DRAFT:
            return 0
        return review_progress(obj)[1]


class VoteOut(Schema):
    weight: float


def expected_answer_of(solution):
    """Réponse attendue, pour aider le relecteur à vérifier la copie : celle des
    paramètres tirés en défi, sinon celle de l'exercice ; vide s'il n'y en a pas."""
    from training.challenges import expected

    session = getattr(solution, "timed_session", None)
    if session is not None and session.challenge_id:
        return expected(session)
    return solution.exercise.final_answer


class ReviewTaskOut(Schema):
    """Relecture à faire. L'auteur de la solution n'est pas montré : relecture anonyme."""

    id: int
    assigned_at: datetime
    solution_id: int
    exercise_id: int
    exercise_title: str
    exercise_statement: str
    primary_level: str
    solution_body: str
    solution_photos: list[PhotoOut]
    expected_answer: str
    ai_usage: str

    @staticmethod
    def resolve_exercise_id(obj):
        return obj.solution.exercise_id

    @staticmethod
    def resolve_expected_answer(obj):
        return expected_answer_of(obj.solution)

    @staticmethod
    def resolve_solution_photos(obj):
        return photos.described(obj.solution)

    @staticmethod
    def resolve_exercise_title(obj):
        return obj.solution.exercise.title

    @staticmethod
    def resolve_exercise_statement(obj):
        # En défi, le relecteur juge sur l'énoncé tiré pour l'auteur.
        return obj.solution.variant_statement or obj.solution.exercise.statement

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


def draft_fields(payload):
    """Valide un brouillon. Renvoie ses champs, ses niveaux et ses chapitres."""
    problems = title_problems(payload.title)
    if problems:
        raise HttpError(422, problems[0])
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
    topics = list(Topic.objects.filter(slug__in=slugs).select_related("parent"))
    if len(topics) != len(slugs):
        raise HttpError(422, "Chapitre inconnu.")
    # Une notion range l'exercice dans son chapitre aussi.
    topics += list({topic.parent for topic in topics if topic.parent and topic.parent not in topics})
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


RELATED_COUNT = 6


@router.get("/exercises/{int:exercise_id}/related", response=list[ExerciseSummary])
def related_exercises(request, exercise_id: int):
    """Exercices proches, pour le bas de la fiche : même notion d'abord, puis même
    chapitre, au même niveau de préférence."""
    exercise = get_object_or_404(
        Exercise.objects.prefetch_related("topics", "levels"),
        pk=exercise_id,
        status__in=[Exercise.Status.PUBLISHED, Exercise.Status.MERGED],
    )
    topics = {topic.pk for topic in exercise.topics.all()}
    notions = {topic.pk for topic in exercise.topics.all() if topic.parent_id is not None}
    levels = {exercise.primary_level_id} | {level.pk for level in exercise.levels.all()}
    if not topics:
        return []
    candidates = (
        published_exercises()
        .filter(topics__in=topics)
        .exclude(pk__in=[exercise.pk, exercise.merged_into_id or 0])
        .distinct()
    )

    def score(other):
        theirs = {topic.pk for topic in other.topics.all()}
        their_levels = {other.primary_level_id} | {level.pk for level in other.levels.all()}
        return (
            -3 * len(notions & theirs) - len(topics & theirs) - 2 * (other.primary_level_id in levels) - bool(levels & their_levels),
            -other.published_at.timestamp(),
        )

    return sorted(candidates, key=score)[:RELATED_COUNT]


@router.post("/exercises", response={201: DraftOut}, auth=django_auth)
def create_exercise(request, payload: ExerciseIn):
    """Crée un brouillon. La publication est une étape à part, qui vérifie les doublons."""
    user = contributor(request)
    fields, levels, topics = draft_fields(payload)
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
    fields, levels, topics = draft_fields(payload)
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
    throttle=[AuthRouteThrottle("ecriture", "30/m")],
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
        status=Solution.Status.UNDER_REVIEW,
    ).exists():
        raise HttpError(409, "Tu as déjà une solution en cours d'évaluation sur cet exercice.")
    upload = pending_upload(user, exercise, payload.photo_upload)
    with transaction.atomic():
        solution = Solution.objects.create(exercise=exercise, author=user, ai_usage=payload.ai_usage)
        # Les photos d'abord : la publication les lit (plagiat, question de compréhension).
        photos.attach(upload, solution)
        publish_solution(solution)
    return 201, solution


# ---------------------------------------------------------------- photos de copie (QR code)


class PhotoUploadOut(Schema):
    """Envoi de photos : ce que montrent l'ordinateur (QR code, photos reçues) et le
    téléphone (exercice, place restante)."""

    token: str
    exercise_id: int
    exercise_title: str
    expires_at: datetime
    open: bool
    max_photos: int
    # Envoi d'une session chronométrée : il se ferme avec le temps imparti.
    timed: bool
    photos: list[PhotoOut]


def _upload_out(upload):
    return photos.upload_state(upload)


def _live_upload(token):
    return get_object_or_404(photos.live_uploads().select_related("exercise", "timed_session"), token=token)


def _image(photo):
    try:
        file = photo.image.open("rb")
    except FileNotFoundError:
        # Fichier absent (sauvegarde restaurée sans ses photos, par exemple) : introuvable, pas une panne.
        raise HttpError(404, "Photo introuvable.")
    response = FileResponse(file, content_type="image/jpeg")
    # Une copie n'a rien à faire dans un cache partagé ; le navigateur la garde une heure.
    response["Cache-Control"] = "private, max-age=3600"
    return response


@router.post(
    "/exercises/{int:exercise_id}/photo-uploads",
    response={201: PhotoUploadOut},
    auth=django_auth,
    throttle=[AuthRouteThrottle("envoi-photos", "30/h")],
)
def open_photo_upload(request, exercise_id: int):
    """Ouvre un envoi de photos : son jeton, dans le QR code, ouvre le dépôt au téléphone."""
    user = contributor(request)
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    return 201, _upload_out(photos.open_upload(user, exercise))


@router.post("/photo-uploads/{token}/reopen", response=PhotoUploadOut, auth=django_auth)
def reopen_photo_upload(request, token: str):
    """QR code expiré : son auteur le prolonge, sans perdre les photos déjà reçues."""
    upload = _live_upload(token)
    if upload.user_id != request.auth.pk:
        raise HttpError(404, "Envoi introuvable.")
    try:
        return _upload_out(photos.reopen(upload))
    except RuleError as error:
        raise HttpError(409, str(error))


@router.get("/photo-uploads/{token}", response=PhotoUploadOut)
def photo_upload(request, token: str):
    """État d'un envoi : le téléphone y dépose, l'ordinateur y voit arriver les photos."""
    return _upload_out(_live_upload(token))


@router.post(
    "/photo-uploads/{token}/photos",
    response={201: PhotoOut},
    throttle=[AnonRouteThrottle("depot-photo", "60/h")],
)
def add_upload_photo(request, token: str, photo: File[UploadedFile]):
    """Dépose une photo, sans compte : le jeton du QR code suffit, pendant 30 minutes ou,
    en session chronométrée, pendant le temps imparti."""
    upload = _live_upload(token)
    if not photos.is_open(upload):
        raise HttpError(410, photos.closed_message(upload))
    if photos.pending(upload).count() >= photos.MAX_PHOTOS:
        raise HttpError(409, f"{photos.MAX_PHOTOS} photos au plus : retire-en une pour en ajouter une autre.")
    if photo.size > photos.MAX_BYTES:
        raise HttpError(413, "Photo trop lourde : 10 Mo au plus.")
    try:
        added = photos.add_photo(upload, photo.read())
    except RuleError as error:
        raise HttpError(422, str(error))
    return 201, {"id": added.pk, "url": photos.upload_photo_url(upload, added), "width": added.width, "height": added.height}


@router.delete("/photo-uploads/{token}/photos/{int:photo_id}", response={204: None})
def remove_upload_photo(request, token: str, photo_id: int):
    try:
        photos.remove_photo(_live_upload(token), photo_id)
    except RuleError as error:
        raise HttpError(404, str(error))
    return 204, None


@router.get("/photo-uploads/{token}/photos/{int:photo_id}")
def upload_photo_file(request, token: str, photo_id: int):
    return _image(get_object_or_404(photos.pending(_live_upload(token)), pk=photo_id))


@router.get("/solutions/{int:solution_id}/photos/{int:photo_id}")
def solution_photo_file(request, solution_id: int, photo_id: int):
    """Photo d'une solution, pour qui peut en lire le texte (voir photos.can_view)."""
    photo = get_object_or_404(
        SolutionPhoto.objects.select_related("solution__author"), pk=photo_id, solution_id=solution_id
    )
    if not photos.can_view(request.user, photo.solution):
        raise HttpError(404, "Photo introuvable.")
    return _image(photo)


@router.get(
    "/exercises/{exercise_id}/my-solutions",
    response=list[MySolutionOut],
    auth=django_auth,
)
def my_solutions(request, exercise_id: int):
    return (
        Solution.objects.filter(exercise_id=exercise_id, author=request.auth)
        .exclude(status=Solution.Status.DRAFT)
        .prefetch_related("reviews", "photos")
        .order_by("-published_at")
    )


@router.post("/exercises/{exercise_id}/vote", response={201: VoteOut}, auth=django_auth)
def vote_for_exercise(request, exercise_id: int):
    """Vote « utile » pour un exercice. Les copies sont privées : on ne vote pas pour elles."""
    user = contributor(request)
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    if Vote.objects.filter(voter=user, exercise=exercise).exists():
        raise HttpError(409, "Tu as déjà voté.")
    try:
        return 201, cast_vote(user, exercise=exercise)
    except IntegrityError:
        raise HttpError(409, "Tu as déjà voté.")


@router.get("/reviews", response=list[ReviewTaskOut], auth=django_auth)
def pending_reviews(request):
    return (
        Review.objects.filter(
            reviewer=request.auth,
            submitted_at=None,
            expired_at=None,
            round=F("solution__review_round"),
            solution__status=Solution.Status.UNDER_REVIEW,
        )
        .select_related("solution__exercise__primary_level")
        .prefetch_related("solution__photos")
        .order_by("assigned_at")
    )


@router.post("/reviews/{int:review_id}", response=ReviewResult, auth=django_auth)
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
    if not feedback:
        # C'est la seule correction que l'auteur recevra : aucune solution n'est publique.
        raise HttpError(
            422,
            "Laisse un commentaire à l'auteur : ce qui est juste, ce qui manque ou ce qui est faux. "
            "C'est la seule correction qu'il recevra.",
        )
    status = submit_review(review, payload.verdict, feedback=feedback)
    return {"solution_status": status}


# ---------------------------------------------------------------- relecture : copies en attente


class OpenSolutionOut(Schema):
    solution_id: int
    exercise_id: int
    exercise_title: str
    primary_level: str
    published_at: datetime | None
    # En relecture depuis (envoi, ou dernière révision), en heures ; et ses relectures.
    waiting_hours: int
    reviews_done: int
    reviews_expected: int


class RevisionIn(Schema):
    # Nouvelles photos de la copie : elles remplacent les précédentes (et un ancien texte).
    photo_upload: str = Field(min_length=1, max_length=64)


# L'équipe voit toutes les copies en attente ; un relecteur, les vingt plus anciennes.
OPEN_FOR_TEAM = 100
OPEN_FOR_REVIEWERS = 20


@router.get("/reviews/open", response=list[OpenSolutionOut], auth=django_auth)
def open_for_review(request):
    """Copies en relecture que l'on peut choisir de relire, les plus anciennes d'abord :
    pour un relecteur, une relecture de plus ; pour l'équipe du site, la décision."""
    user = contributor(request)
    if not can_review(user):
        return []
    solutions = (
        Solution.objects.filter(status=Solution.Status.UNDER_REVIEW)
        .exclude(author=user)
        .exclude(author_id__in=linked_ids(user))
        .exclude(reviews__reviewer=user)
        .select_related("exercise__primary_level")
        .order_by("updated_at")[: OPEN_FOR_TEAM if is_moderator(user) else OPEN_FOR_REVIEWERS]
    )
    now = timezone.now()
    items = []
    for solution in solutions:
        done, expected = review_progress(solution)
        items.append(
            {
                "solution_id": solution.pk,
                "exercise_id": solution.exercise_id,
                "exercise_title": solution.exercise.title,
                "primary_level": solution.exercise.primary_level.code,
                "published_at": solution.published_at,
                "waiting_hours": int((now - solution.updated_at).total_seconds() // 3600),
                "reviews_done": done,
                "reviews_expected": expected,
            }
        )
    return items


@router.post("/solutions/{int:solution_id}/volunteer", response={201: ReviewTaskOut}, auth=django_auth)
def volunteer(request, solution_id: int):
    user = contributor(request)
    solution = get_object_or_404(Solution.objects.select_related("exercise__primary_level"), pk=solution_id)
    return 201, volunteer_review(solution, user)


@router.post("/solutions/{int:solution_id}/revise", response=MySolutionOut, auth=django_auth)
def revise(request, solution_id: int, payload: RevisionIn):
    """Révision par l'auteur, à compléter ou validée : de nouvelles photos de la copie,
    qui repart en relecture."""
    user = contributor(request)
    solution = get_object_or_404(Solution.objects.select_related("exercise"), pk=solution_id, author=user)
    upload = pending_upload(user, solution.exercise, payload.photo_upload)
    revised, _ = revise_solution(solution, "", upload=upload)
    return revised
