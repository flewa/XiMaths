"""API des notifications."""

from datetime import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle
from pydantic import Field

from . import push
from .models import Notification, PushSubscription
from .services import unsubscribe

router = Router(tags=["notifications"])
PAGE_SIZE = 50


class NotificationOut(Schema):
    id: int
    kind: str
    title: str
    body: str
    url: str
    created_at: datetime
    read: bool

    @staticmethod
    def resolve_read(obj):
        return obj.read_at is not None


class NotificationsOut(Schema):
    unread: int
    items: list[NotificationOut]


@router.get("/notifications", response=NotificationsOut, auth=django_auth)
def list_notifications(request):
    mine = Notification.objects.filter(user=request.auth)
    return {"unread": mine.filter(read_at=None).count(), "items": mine[:PAGE_SIZE]}


@router.post("/notifications/read", response={204: None}, auth=django_auth)
def read_all(request):
    Notification.objects.filter(user=request.auth, read_at=None).update(read_at=timezone.now())
    return 204, None


@router.post("/notifications/{int:notification_id}/read", response={204: None}, auth=django_auth)
def read_one(request, notification_id: int):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.auth)
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return 204, None


@router.get("/notifications/unsubscribe")
def unsubscribe_view(request, token: str = ""):
    """Lien des emails : désabonne sans connexion, puis affiche une confirmation."""
    user = unsubscribe(token)
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/desabonnement?{'ok=1' if user else 'erreur=1'}")


# ---------------------------------------------------------------- Web Push


class PushKeyOut(Schema):
    # null : le Web Push n'est pas configuré, le réglage ne s'affiche pas.
    public_key: str | None


class PushKeysIn(Schema):
    p256dh: str = Field(max_length=200)
    auth: str = Field(max_length=100)


class PushSubscriptionIn(Schema):
    """Le PushSubscription.toJSON() du navigateur."""

    endpoint: str = Field(max_length=1000)
    keys: PushKeysIn


class EndpointIn(Schema):
    endpoint: str = Field(max_length=1000)


@router.get("/push/key", response=PushKeyOut)
def push_key(request):
    """Clé publique VAPID, pour que le navigateur s'abonne."""
    return {"public_key": settings.VAPID_PUBLIC_KEY if push.enabled() else None}


@router.post(
    "/push/subscriptions",
    response={204: None},
    auth=django_auth,
    throttle=[AuthRateThrottle("30/h")],
)
def push_subscribe(request, payload: PushSubscriptionIn):
    """Active les notifications push sur ce navigateur : une par jour au plus, jamais
    entre 22 h et 8 h."""
    if not push.enabled():
        raise HttpError(404, "Les notifications push ne sont pas configurées.")
    if not push.allowed_endpoint(payload.endpoint):
        raise HttpError(422, "Service de notifications inconnu.")
    if not push.valid_keys(payload.keys.p256dh, payload.keys.auth):
        raise HttpError(422, "Clés d'abonnement invalides.")
    push.subscribe(request.auth, payload.endpoint, payload.keys.p256dh, payload.keys.auth)
    return 204, None


class PushStatusOut(Schema):
    active: bool


@router.post("/push/status", response=PushStatusOut, auth=django_auth)
def push_status(request, payload: EndpointIn):
    """L'abonnement de ce navigateur est-il celui de ce compte ? Un navigateur partagé
    peut être abonné pour un autre compte."""
    return {"active": PushSubscription.objects.filter(user=request.auth, endpoint=payload.endpoint).exists()}


@router.post("/push/unsubscribe", response={204: None}, auth=django_auth)
def push_unsubscribe(request, payload: EndpointIn):
    PushSubscription.objects.filter(user=request.auth, endpoint=payload.endpoint).delete()
    return 204, None
