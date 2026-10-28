"""API de la progression : classements, badges et profils publics."""

from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import HttpError

from catalog.models import Level
from content.models import Exercise, Solution

from .badges import BADGES, BADGES_BY_SLUG
from .models import UserBadge
from .rankings import TOP_SIZE, Week, absence_reason, neighbourhood, standings
from .services import balance

router = Router(tags=["progression"])
User = get_user_model()

GLOBAL = "global"
PANTHEON = "pantheon"


class EntryOut(Schema):
    rank: int
    username: str
    declared_level: str | None
    points: int
    is_me: bool


class MyPositionOut(Schema):
    rank: int | None
    points: int | None
    message: str | None = None
    # Voisins de chaque côté, quand le visiteur est hors du top 50.
    neighbours: list[EntryOut] = []


class LeaderboardOut(Schema):
    board: str
    board_label: str
    week: str | None
    week_start: date | None
    week_end: date | None
    final: bool
    previous_week: str | None
    next_week: str | None
    peers_level: str | None
    total: int
    top: list[EntryOut]
    me: MyPositionOut | None


class BadgeOut(Schema):
    slug: str
    name: str
    criterion: str
    available: bool
    holders: int
    awarded_at: datetime | None


class EarnedBadgeOut(Schema):
    slug: str
    name: str
    criterion: str
    awarded_at: datetime


class MemberOut(Schema):
    username: str
    declared_level: str | None
    trust_level: str
    joined: date
    # Absents si le membre a masqué sa présence dans les classements.
    points: int | None
    exercises_published: int
    solutions_validated: int
    badges: list[EarnedBadgeOut]


def _viewer(request):
    return request.user if request.user.is_authenticated else None


@router.get("/leaderboards", response=LeaderboardOut)
def leaderboard(request, board: str = GLOBAL, week: str | None = None, peers: bool = False):
    """Classement hebdomadaire global ou par niveau (code du niveau), ou Panthéon des
    points cumulés. Top 50, puis la position du visiteur et ses 5 voisins de chaque côté.
    `peers` : seulement ceux qui ont déclaré le même niveau que le visiteur."""
    viewer = _viewer(request)
    level = current = None
    if board != PANTHEON:
        if board != GLOBAL:
            level = Level.objects.filter(code=board).first()
            if level is None:
                raise HttpError(404, "Classement inconnu.")
        try:
            current = Week.parse(week) if week else Week.containing()
        except ValueError:
            raise HttpError(422, "Semaine invalide : format attendu 2026-W44.")
    peers_level = viewer.declared_level if peers and viewer and viewer.declared_level_id else None
    entries = standings(week=current, level=level, peers_level=peers_level)

    viewer_id = viewer.pk if viewer else None

    def out(entry):
        return {
            "rank": entry.rank,
            "username": entry.username,
            "declared_level": entry.declared_level,
            "points": entry.points,
            "is_me": entry.user_id == viewer_id,
        }

    me = None
    if viewer:
        index, around = neighbourhood(entries, viewer.pk)
        if index is None:
            where = f"en {level.code}" if level else ""
            me = {"rank": None, "points": None, "message": absence_reason(viewer, week=current, where=where)}
        else:
            me = {
                "rank": entries[index].rank,
                "points": entries[index].points,
                "neighbours": [out(entry) for entry in around] if index >= TOP_SIZE else [],
            }

    following = current.shifted(1) if current else None
    return {
        "board": board,
        "board_label": "Panthéon" if board == PANTHEON else (level.name if level else "Global"),
        "week": current.label if current else None,
        "week_start": current.monday if current else None,
        "week_end": current.sunday if current else None,
        "final": current.is_final() if current else False,
        "previous_week": current.shifted(-1).label if current else None,
        "next_week": following.label if following and following <= Week.containing() else None,
        "peers_level": peers_level.code if peers_level else None,
        "total": len(entries),
        "top": [out(entry) for entry in entries[:TOP_SIZE]],
        "me": me,
    }


@router.get("/badges", response=list[BadgeOut])
def list_badges(request):
    """Tous les badges, avec leur critère, le nombre de détenteurs et ta date d'obtention."""
    viewer = _viewer(request)
    holders = dict(UserBadge.objects.values("badge").annotate(n=Count("pk")).values_list("badge", "n"))
    mine = (
        dict(UserBadge.objects.filter(user=viewer).values_list("badge", "awarded_at")) if viewer else {}
    )
    return [
        {
            "slug": badge.slug,
            "name": badge.name,
            "criterion": badge.criterion,
            "available": badge.earned is not None,
            "holders": holders.get(badge.slug, 0),
            "awarded_at": mine.get(badge.slug),
        }
        for badge in BADGES
    ]


@router.get("/members/{username}", response=MemberOut)
def member(request, username: str):
    user = get_object_or_404(User.objects.select_related("declared_level"), username=username, is_active=True)
    return {
        "username": user.username,
        "declared_level": user.declared_level.code if user.declared_level else None,
        "trust_level": User.TrustLevel(user.trust_level).label,
        "joined": user.date_joined.date(),
        "points": balance(user) if user.leaderboard_visible else None,
        "exercises_published": Exercise.objects.filter(
            author=user, status=Exercise.Status.PUBLISHED
        ).count(),
        "solutions_validated": Solution.objects.filter(
            author=user, status=Solution.Status.VALIDATED
        ).count(),
        "badges": [
            {
                "slug": earned.badge,
                "name": BADGES_BY_SLUG[earned.badge].name,
                "criterion": BADGES_BY_SLUG[earned.badge].criterion,
                "awarded_at": earned.awarded_at,
            }
            for earned in user.badges.all()
            if earned.badge in BADGES_BY_SLUG
        ],
    }
