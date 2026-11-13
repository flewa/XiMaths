"""Panneau d'administration : ce que les administrateurs du site voient d'un coup d'œil.

Une vue d'ensemble chiffrée, puis trois listes à filtrer : toutes les copies (en relecture,
validées, à reprendre, masquées), avec leurs relectures et leurs points ; les membres ; les
exercices. Le panneau montre ; les décisions se prennent ailleurs, là où elles sont motivées
et inscrites au journal (page Modération, page Relectures).

Réservé aux administrateurs (is_staff). Les copies restent privées pour tous les autres : ce
panneau est la vue de l'équipe qui en répond. Aucune adresse email n'y figure.
"""

from datetime import date, datetime, timedelta
from typing import Literal

from django.contrib.auth import get_user_model
from django.db.models import Count, F, IntegerField, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth

from accounts.permissions import is_moderator
from accounts.profile import trust_label
from gamification.models import PointTransaction
from moderation.services import pending_counts
from training.models import TimedSession

from . import photos
from .api import PhotoOut
from .models import Exercise, ExerciseRead, Message, Review, Solution
from .services import REVIEWERS_PER_SOLUTION, TEAM_ALERT_AFTER, can_review, waiting_solutions

User = get_user_model()
router = Router(tags=["administration"])

PAGE_SIZE = 30
WEEK = timedelta(days=7)
DAYS_SHOWN = 14
Status = Solution.Status
SENT = [Status.UNDER_REVIEW, Status.VALIDATED, Status.NEEDS_WORK, Status.HIDDEN]


def admin(request):
    """Le panneau est réservé aux administrateurs du site."""
    user = request.auth
    if not user.is_staff:
        raise HttpError(403, "Réservé aux administrateurs du site.")
    return user


def paginate(queryset, page):
    """(éléments de la page, total, page retenue, nombre de pages)."""
    total = queryset.count()
    pages = max(1, -(-total // PAGE_SIZE))
    page = min(max(page, 1), pages)
    return list(queryset[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]), total, page, pages


class PageOut(Schema):
    total: int
    page: int
    pages: int


# ---------------------------------------------------------------- vue d'ensemble


class DayOut(Schema):
    date: date
    signups: int
    solutions: int
    reviews: int


class OverviewOut(Schema):
    members: int
    members_week: int
    # Membres qui ont lu, envoyé, relu, publié ou écrit quelque chose en 7 jours.
    members_active_week: int
    # Membres qui peuvent être tirés au sort pour relire.
    reviewers: int
    exercises: int
    exercises_week: int
    under_review: int
    validated: int
    needs_work: int
    hidden: int
    solutions_week: int
    # Copies en relecture depuis plus de 72 heures : l'équipe peut les corriger elle-même.
    late: int
    reviews_week: int
    messages_week: int
    # Files de modération : signalements, messages signalés, appels.
    moderation_pending: int
    # Les 14 derniers jours, du plus ancien au plus récent.
    days: list[DayOut]


def per_day(queryset, field, since):
    rows = (
        queryset.filter(**{f"{field}__gte": since})
        .annotate(day=TruncDate(field))
        .values("day")
        .annotate(count=Count("pk"))
    )
    return {row["day"]: row["count"] for row in rows}


@router.get("/panel/overview", response=OverviewOut, auth=django_auth)
def overview(request):
    admin(request)
    now = timezone.now()
    week = now - WEEK
    members = User.objects.filter(is_active=True)
    by_status = dict(Solution.objects.filter(status__in=SENT).values_list("status").annotate(count=Count("pk")))
    active = set()
    for queryset, field, stamp in [
        (Solution.objects.exclude(status=Status.DRAFT), "author_id", "published_at"),
        (Review.objects.all(), "reviewer_id", "submitted_at"),
        (Message.objects.all(), "author_id", "created_at"),
        (Exercise.objects.all(), "author_id", "published_at"),
        (ExerciseRead.objects.all(), "user_id", "first_read_at"),
    ]:
        active.update(queryset.filter(**{f"{stamp}__gte": week}).values_list(field, flat=True))
    active.discard(None)

    today = timezone.localdate(now)
    first = today - timedelta(days=DAYS_SHOWN - 1)
    since = timezone.make_aware(datetime.combine(first, datetime.min.time()))
    signups = per_day(members, "date_joined", since)
    sent = per_day(Solution.objects.exclude(status=Status.DRAFT), "published_at", since)
    reviewed = per_day(Review.objects.all(), "submitted_at", since)
    days = [first + timedelta(days=offset) for offset in range(DAYS_SHOWN)]

    counts = pending_counts()
    return {
        "members": members.count(),
        "members_week": members.filter(date_joined__gte=week).count(),
        "members_active_week": members.filter(pk__in=active).count(),
        "reviewers": sum(can_review(member) for member in members.filter(Q(trust_level__gte=2) | Q(is_staff=True) | Q(verified_teacher=True))),
        "exercises": Exercise.objects.filter(status=Exercise.Status.PUBLISHED).count(),
        "exercises_week": Exercise.objects.filter(status=Exercise.Status.PUBLISHED, published_at__gte=week).count(),
        "under_review": by_status.get(Status.UNDER_REVIEW, 0),
        "validated": by_status.get(Status.VALIDATED, 0),
        "needs_work": by_status.get(Status.NEEDS_WORK, 0),
        "hidden": by_status.get(Status.HIDDEN, 0),
        "solutions_week": Solution.objects.exclude(status=Status.DRAFT).filter(published_at__gte=week).count(),
        "late": waiting_solutions(now=now).count(),
        "reviews_week": Review.objects.filter(submitted_at__gte=week).count(),
        "messages_week": Message.objects.filter(created_at__gte=week).count(),
        "moderation_pending": counts["reports"] + counts["messages"] + counts["appeals"],
        "days": [
            {"date": day, "signups": signups.get(day, 0), "solutions": sent.get(day, 0), "reviews": reviewed.get(day, 0)}
            for day in days
        ],
    }


# ---------------------------------------------------------------- copies


class PanelReviewOut(Schema):
    reviewer: str
    # Relecture de l'équipe : elle vaut décision à elle seule.
    team: bool
    # Tirée au sort (sinon : relecture choisie).
    assigned: bool
    verdict: str
    verdict_label: str
    feedback: str
    assigned_at: datetime
    submitted_at: datetime | None
    # Non rendue à 72 h : confiée à quelqu'un d'autre.
    expired: bool


class PanelSolutionOut(Schema):
    id: int
    exercise_id: int
    exercise_title: str
    author: str | None
    status: str
    status_label: str
    origin: str
    origin_label: str
    ai_usage: str
    ai_usage_label: str
    published_at: datetime | None
    validated_at: datetime | None
    # En relecture : depuis combien d'heures (depuis l'envoi, ou la dernière révision).
    waiting_hours: int | None
    # Attend l'équipe : plus de 72 heures en relecture, ou pas assez de relecteurs.
    late: bool
    # Moins de relecteurs que le consensus n'en demande : l'équipe doit la corriger.
    short_staffed: bool
    review_round: int
    reviews_done: int
    reviews_expected: int
    reviews: list[PanelReviewOut]
    # Points que cette copie a rapportés à son auteur, annulations déduites.
    points: int
    photos: list[PhotoOut]
    is_model: bool
    after_model: bool
    # L'administrateur peut la corriger lui-même : sa relecture vaut décision.
    can_take: bool


class SolutionPageOut(PageOut):
    items: list[PanelSolutionOut]


SolutionFilter = Literal["", "under_review", "late", "validated", "needs_work", "hidden"]


def points_by_source(model, ids, authors):
    """Points nets crédités aux auteurs depuis ces objets : {identifiant: total}."""
    if not ids:
        return {}
    rows = (
        PointTransaction.objects.filter(source_type=model._meta.label_lower, source_id__in=ids, user_id__in=authors)
        .values("source_id", "user_id")
        .annotate(total=Sum("amount"))
    )
    return {(row["source_id"], row["user_id"]): row["total"] for row in rows}


@router.get("/panel/solutions", response=SolutionPageOut, auth=django_auth)
def solutions(request, status: SolutionFilter = "", q: str = "", page: int = 1):
    """Toutes les copies envoyées. En relecture : les plus anciennes d'abord ; sinon les
    plus récentes d'abord."""
    me = admin(request)
    now = timezone.now()
    queryset = Solution.objects.filter(status__in=SENT)
    if status == "late":
        queryset = waiting_solutions(now=now)
    elif status:
        queryset = queryset.filter(status=status)
    q = q.strip()
    if q:
        queryset = queryset.filter(Q(exercise__title__icontains=q) | Q(author__username__icontains=q))
    waiting = status in ("under_review", "late")
    queryset = queryset.select_related("exercise", "author").order_by("updated_at" if waiting else "-published_at", "-pk")
    items, total, page, pages = paginate(queryset, page)

    ids = [solution.pk for solution in items]
    authors = {solution.author_id for solution in items if solution.author_id}
    reviews = {}
    for review in Review.objects.filter(solution_id__in=ids).select_related("reviewer").order_by("assigned_at"):
        reviews.setdefault(review.solution_id, []).append(review)
    sessions = dict(TimedSession.objects.filter(solution_id__in=ids).values_list("solution_id", "pk"))
    own = points_by_source(Solution, ids, authors)
    timed = points_by_source(TimedSession, list(sessions.values()), authors)

    out = []
    for solution in items:
        current = [review for review in reviews.get(solution.pk, []) if review.round == solution.review_round]
        done = sum(review.submitted_at is not None for review in current)
        drawn = sum(review.assigned and review.expired_at is None for review in current)
        chosen = sum(not review.assigned for review in current)
        in_review = solution.status == Status.UNDER_REVIEW
        hours = int((now - solution.updated_at).total_seconds() // 3600) if in_review else None
        points = own.get((solution.pk, solution.author_id), 0)
        if solution.pk in sessions:
            points += timed.get((sessions[solution.pk], solution.author_id), 0)
        out.append(
            {
                "id": solution.pk,
                "exercise_id": solution.exercise_id,
                "exercise_title": solution.exercise.title,
                "author": solution.author.username if solution.author else None,
                "status": solution.status,
                "status_label": solution.get_status_display(),
                "origin": solution.origin,
                "origin_label": solution.get_origin_display(),
                "ai_usage": solution.ai_usage,
                "ai_usage_label": solution.get_ai_usage_display(),
                "published_at": solution.published_at,
                "validated_at": solution.validated_at,
                "waiting_hours": hours,
                "late": bool(in_review and (now - solution.updated_at >= TEAM_ALERT_AFTER or drawn + chosen < REVIEWERS_PER_SOLUTION)),
                "short_staffed": bool(in_review and drawn + chosen < REVIEWERS_PER_SOLUTION),
                "review_round": solution.review_round,
                "reviews_done": done,
                "reviews_expected": max(drawn + chosen, REVIEWERS_PER_SOLUTION),
                "reviews": [
                    {
                        "reviewer": review.reviewer.username,
                        "team": is_moderator(review.reviewer),
                        "assigned": review.assigned,
                        "verdict": review.verdict,
                        "verdict_label": review.get_verdict_display() if review.verdict else "",
                        "feedback": review.feedback,
                        "assigned_at": review.assigned_at,
                        "submitted_at": review.submitted_at,
                        "expired": review.expired_at is not None,
                    }
                    for review in current
                ],
                "points": points,
                "photos": photos.described(solution),
                "is_model": solution.model_at is not None and solution.model_consent and solution.status == Status.VALIDATED,
                "after_model": solution.after_model,
                "can_take": in_review
                and solution.author_id != me.pk
                and not any(review.reviewer_id == me.pk for review in reviews.get(solution.pk, [])),
            }
        )
    return {"total": total, "page": page, "pages": pages, "items": out}


# ---------------------------------------------------------------- membres


class PanelMemberOut(Schema):
    username: str
    joined_at: datetime
    last_login: datetime | None
    status: str
    status_label: str
    trust_label: str
    is_staff: bool
    is_moderator: bool
    email_verified: bool
    points: int
    exercises: int
    solutions: int
    validated: int
    reviews: int


class MemberPageOut(PageOut):
    items: list[PanelMemberOut]


MemberFilter = Literal["", "team", "sanctioned", "unverified"]

# Colonnes triables : clé d'adresse → champ. Un clic trie d'abord du plus grand au plus petit
# (le plus récent d'abord pour une date), sauf le pseudo, dans l'ordre alphabétique.
MEMBER_SORTS = {
    "inscription": "date_joined",
    "pseudo": "username",
    "points": "points_total",
    "exercices": "exercises_count",
    "copies": "validated_count",
    "relectures": "reviews_count",
    "connexion": "last_login",
}
EXERCISE_SORTS = {
    "publication": "published_at",
    "titre": "title",
    "lectures": "readers_count",
    "copies": "validated_count",
    "relecture": "review_count",
    "messages": "messages_count",
    "difficulte": "difficulty",
}
Direction = Literal["asc", "desc"]


def sorted_by(queryset, sorts, key, direction, default):
    """Trie sur une colonne connue (les vides en dernier), départage par identifiant."""
    field = sorts.get(key)
    if field is None:
        return queryset.order_by(*default)
    expression = F(field).asc(nulls_last=True) if direction == "asc" else F(field).desc(nulls_last=True)
    return queryset.order_by(expression, "-pk")


def counted(model, owner, **filters):
    """Nombre d'objets de `model` rattachés au membre, en sous-requête (sans jointure)."""
    rows = model.objects.filter(**{owner: OuterRef("pk")}, **filters).order_by().values(owner).annotate(n=Count("pk")).values("n")
    return Coalesce(Subquery(rows, output_field=IntegerField()), 0)


@router.get("/panel/members", response=MemberPageOut, auth=django_auth)
def members(
    request, show: MemberFilter = "", q: str = "", page: int = 1, sort: str = "", direction: Direction = "desc"
):
    """Les membres, les derniers inscrits d'abord, ou triés sur une colonne."""
    admin(request)
    queryset = User.objects.filter(is_active=True)
    if show == "team":
        queryset = queryset.filter(Q(is_staff=True) | Q(trust_level__gte=User.TrustLevel.MODERATOR))
    elif show == "sanctioned":
        queryset = queryset.exclude(status=User.Status.ACTIVE)
    elif show == "unverified":
        queryset = queryset.filter(email_verified_at=None)
    q = q.strip()
    if q:
        queryset = queryset.filter(username__icontains=q)
    points = (
        PointTransaction.objects.filter(user=OuterRef("pk")).order_by().values("user").annotate(total=Sum("amount")).values("total")
    )
    queryset = queryset.annotate(
        points_total=Coalesce(Subquery(points, output_field=IntegerField()), 0),
        exercises_count=counted(Exercise, "author", status=Exercise.Status.PUBLISHED),
        solutions_count=counted(Solution, "author", status__in=SENT),
        validated_count=counted(Solution, "author", status=Status.VALIDATED),
        reviews_count=counted(Review, "reviewer", submitted_at__isnull=False),
    )
    queryset = sorted_by(queryset, MEMBER_SORTS, sort, direction, ["-date_joined", "-pk"])
    items, total, page, pages = paginate(queryset, page)
    return {
        "total": total,
        "page": page,
        "pages": pages,
        "items": [
            {
                "username": member.username,
                "joined_at": member.date_joined,
                "last_login": member.last_login,
                "status": member.status,
                "status_label": member.get_status_display(),
                "trust_label": trust_label(member),
                "is_staff": member.is_staff,
                "is_moderator": is_moderator(member),
                "email_verified": member.email_verified_at is not None,
                "points": member.points_total,
                "exercises": member.exercises_count,
                "solutions": member.solutions_count,
                "validated": member.validated_count,
                "reviews": member.reviews_count,
            }
            for member in items
        ],
    }


# ---------------------------------------------------------------- exercices


class PanelExerciseOut(Schema):
    id: int
    title: str
    author: str | None
    status: str
    status_label: str
    primary_level: str
    difficulty: int
    published_at: datetime | None
    solutions: int
    validated: int
    under_review: int
    readers: int
    messages: int


class ExercisePageOut(PageOut):
    items: list[PanelExerciseOut]


ExerciseFilter = Literal["", "published", "draft", "removed", "merged", "unsolved"]


@router.get("/panel/exercises", response=ExercisePageOut, auth=django_auth)
def exercises(
    request, status: ExerciseFilter = "", q: str = "", page: int = 1, sort: str = "", direction: Direction = "desc"
):
    """Les exercices, quel que soit leur statut, les plus récents d'abord, ou triés sur une colonne."""
    admin(request)
    queryset = Exercise.objects.all()
    if status == "unsolved":
        queryset = queryset.filter(status=Exercise.Status.PUBLISHED).exclude(solutions__status=Status.VALIDATED)
    elif status:
        queryset = queryset.filter(status=status)
    q = q.strip()
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(author__username__icontains=q))
    queryset = (
        queryset.select_related("author", "primary_level")
        .annotate(
            sent_count=counted(Solution, "exercise", status__in=SENT),
            validated_count=counted(Solution, "exercise", status=Status.VALIDATED),
            review_count=counted(Solution, "exercise", status=Status.UNDER_REVIEW),
            reads_count=counted(ExerciseRead, "exercise"),
            messages_count=counted(Message, "exercise", removed_at__isnull=True),
        )
        .annotate(readers_count=F("visitor_reads") + F("reads_count"))
    )
    queryset = sorted_by(queryset, EXERCISE_SORTS, sort, direction, ["-created_at", "-pk"])
    items, total, page, pages = paginate(queryset, page)
    return {
        "total": total,
        "page": page,
        "pages": pages,
        "items": [
            {
                "id": exercise.pk,
                "title": exercise.title,
                "author": exercise.author.username if exercise.author else None,
                "status": exercise.status,
                "status_label": exercise.get_status_display(),
                "primary_level": exercise.primary_level.code,
                "difficulty": exercise.difficulty,
                "published_at": exercise.published_at,
                "solutions": exercise.sent_count,
                "validated": exercise.validated_count,
                "under_review": exercise.review_count,
                "readers": exercise.readers_count,
                "messages": exercise.messages_count,
            }
            for exercise in items
        ],
    }
