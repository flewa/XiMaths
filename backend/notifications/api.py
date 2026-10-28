"""API des notifications."""

from datetime import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema
from ninja.security import django_auth

from .models import Notification
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
