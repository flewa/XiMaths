"""Questions et remarques sous un exercice : un fil par exercice, lisible par tous, où
l'on écrit une fois connecté. On y demande une précision, on signale une coquille, on
discute d'une méthode ; on n'y donne pas la solution, qui s'envoie en copie. L'équipe du
site retire ce qui n'a rien à faire là, et tout membre peut lui signaler un message."""

from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Field, Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth

from accounts.permissions import contributor, is_moderator
from accounts.schemas import MemberRefOut
from config.throttles import AuthRouteThrottle
from notifications.models import Notification
from notifications.services import notify

from .api import reject_forbidden_latex
from .models import Exercise, Message, MessageFlag

User = get_user_model()
router = Router(tags=["discussion"])
Kind = Notification.Kind


class MessageIn(Schema):
    body: str = Field(min_length=1, max_length=Message.MAX_LENGTH)
    # Le message auquel on répond ; absent pour une nouvelle question.
    parent: int | None = None


class ReplyOut(Schema):
    id: int
    author: MemberRefOut | None
    # L'équipe du site, et l'auteur de l'exercice : leurs réponses comptent double pour qui lit.
    team: bool
    exercise_author: bool
    body: str
    created_at: datetime
    removed: bool
    mine: bool
    can_remove: bool
    flagged: bool


class MessageOut(ReplyOut):
    replies: list[ReplyOut]


def describe(message, exercise, user, flagged):
    removed = message.removed_at is not None
    author = message.author if message.author and message.author.is_active else None
    mine = user.is_authenticated and message.author_id == user.pk
    return {
        "id": message.pk,
        "author": None if removed else author,
        "team": bool(author and not removed and is_moderator(author)),
        "exercise_author": bool(author and not removed and exercise.author_id == author.pk),
        "body": "" if removed else message.body,
        "created_at": message.created_at,
        "removed": removed,
        "mine": bool(mine and not removed),
        "can_remove": bool(not removed and user.is_authenticated and (mine or is_moderator(user))),
        "flagged": message.pk in flagged,
    }


def thread(exercise, user):
    """Le fil de l'exercice, du plus ancien au plus récent. Une réponse retirée disparaît ;
    une question retirée ne reste, vidée, que si des réponses la suivent."""
    messages = list(Message.objects.filter(exercise=exercise).select_related("author"))
    flagged = set()
    if user.is_authenticated:
        flagged = set(MessageFlag.objects.filter(user=user, message__exercise=exercise).values_list("message_id", flat=True))
    replies = {}
    for message in messages:
        if message.parent_id and message.removed_at is None:
            replies.setdefault(message.parent_id, []).append(describe(message, exercise, user, flagged))
    out = []
    for message in messages:
        if message.parent_id:
            continue
        answers = replies.get(message.pk, [])
        if message.removed_at is not None and not answers:
            continue
        out.append({**describe(message, exercise, user, flagged), "replies": answers})
    return out


def team_members():
    return User.objects.filter(is_active=True, status=User.Status.ACTIVE).filter(
        Q(is_staff=True) | Q(trust_level__gte=User.TrustLevel.MODERATOR)
    )


def excerpt(text, length=140):
    text = " ".join(text.split())
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"


@router.get("/exercises/{int:exercise_id}/messages", response=list[MessageOut])
def list_messages(request, exercise_id: int):
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    return thread(exercise, request.user)


@router.post(
    "/exercises/{int:exercise_id}/messages",
    response={201: list[MessageOut]},
    auth=django_auth,
    throttle=[AuthRouteThrottle("discussion", "20/h")],
)
def post_message(request, exercise_id: int, payload: MessageIn):
    user = contributor(request)
    exercise = get_object_or_404(Exercise, pk=exercise_id, status=Exercise.Status.PUBLISHED)
    body = payload.body.strip()
    if len(body) < 2:
        raise HttpError(422, "Écris ton message.")
    reject_forbidden_latex([("le message", body)])
    parent = None
    if payload.parent is not None:
        parent = get_object_or_404(Message, pk=payload.parent, exercise=exercise, removed_at=None)
        # Un seul niveau : répondre à une réponse, c'est répondre à sa question.
        parent = parent.parent or parent
    with transaction.atomic():
        message = Message.objects.create(exercise=exercise, author=user, parent=parent, body=body)
        url = f"/exercices/{exercise.pk}#discussion"
        if parent is None:
            if exercise.author_id != user.pk:
                notify(exercise.author, Kind.DISCUSSION, f"Une question sous ton exercice « {exercise.title} »", excerpt(body), url)
        else:
            # L'auteur de la question, et ceux qui lui ont déjà répondu : une fois chacun.
            people = {parent.author_id, *parent.replies.filter(removed_at=None).values_list("author_id", flat=True)}
            people -= {user.pk, None}
            for member in User.objects.filter(pk__in=people):
                notify(member, Kind.DISCUSSION, f"Une réponse sous « {exercise.title} »", excerpt(body), url)
    return 201, thread(exercise, user)


@router.delete("/messages/{int:message_id}", response=list[MessageOut], auth=django_auth)
def remove_message(request, message_id: int):
    """Retire un message : son auteur, ou l'équipe du site. Le texte reste en base, pour
    qu'un retrait par l'équipe puisse être expliqué ; il n'est plus montré à personne."""
    user = request.auth
    message = get_object_or_404(Message.objects.select_related("exercise", "author"), pk=message_id, removed_at=None)
    mine = message.author_id == user.pk
    if not mine and not is_moderator(user):
        raise HttpError(403, "Tu ne peux retirer que tes propres messages.")
    with transaction.atomic():
        message.removed_at = timezone.now()
        message.removed_by_team = not mine
        message.save(update_fields=["removed_at", "removed_by_team"])
        if not mine:
            notify(
                message.author,
                Kind.DISCUSSION,
                f"Ton message sous « {message.exercise.title} » a été retiré",
                "L'équipe l'a retiré : le fil sert aux questions et aux remarques sur l'énoncé, "
                "pas aux solutions ni aux échanges hors sujet. Ce n'est pas une sanction.",
                f"/exercices/{message.exercise_id}#discussion",
            )
    return thread(message.exercise, user)


@router.post(
    "/messages/{int:message_id}/flag",
    response={204: None},
    auth=django_auth,
    throttle=[AuthRouteThrottle("signalement-message", "20/h")],
)
def flag_message(request, message_id: int):
    """Signale un message à l'équipe. Elle est prévenue au premier signalement."""
    user = contributor(request)
    message = get_object_or_404(Message.objects.select_related("exercise"), pk=message_id, removed_at=None)
    if message.author_id == user.pk:
        raise HttpError(409, "C'est ton message : tu peux le retirer toi-même.")
    try:
        with transaction.atomic():
            MessageFlag.objects.create(message=message, user=user)
    except IntegrityError:
        return 204, None
    if message.flags.count() == 1:
        for member in team_members().exclude(pk=user.pk):
            notify(
                member,
                Kind.DISCUSSION,
                f"Message signalé sous « {message.exercise.title} »",
                excerpt(message.body),
                f"/exercices/{message.exercise_id}#discussion",
                email=True,
            )
    return 204, None
