"""Web Push, via la PWA : une notification par jour au plus, jamais en heures calmes.

Seuls partent en push les types qui attendent une action du membre ou lui apprennent
un résultat (PUSH_KINDS) ; les autres restent dans l'application et, s'il le faut, par
email. Plusieurs notifications en attente partent en un seul message qui les résume :
c'est le cas à 8 h, pour celles retenues pendant la nuit.

Le serveur n'envoie qu'aux services de push des navigateurs (PUSH_HOSTS) : l'adresse
d'un abonnement vient du navigateur, et ne doit pas permettre d'appeler n'importe quel
hôte depuis le serveur.
"""

import base64
import binascii
import json
import logging
from datetime import datetime, time, timedelta
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from pywebpush import WebPushException, webpush

from .models import Notification, PushSubscription

logger = logging.getLogger(__name__)
Kind = Notification.Kind

PUSH_KINDS = {
    Kind.REVIEW_ASSIGNED,
    Kind.REVIEW_REMINDER,
    Kind.SOLUTION_VALIDATED,
    Kind.SOLUTION_NEEDS_WORK,
    Kind.EXERCISE_SOLVED,
    Kind.COMPREHENSION_QUESTION,
    Kind.CHALLENGE,
    Kind.GOAL,
}
# Une notification plus ancienne n'est plus une nouvelle : elle reste dans l'application.
PENDING_WINDOW = timedelta(hours=24)
PUSH_HOSTS = (
    "fcm.googleapis.com",  # Chrome, Android
    "updates.push.services.mozilla.com",  # Firefox
    "push.apple.com",  # Safari
    "notify.windows.com",  # Edge
)
MAX_DEVICES = 10
TTL = 12 * 3600
TIMEOUT = 5
BODY_MAX = 180


def enabled():
    return bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY)


def allowed_endpoint(url):
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return (
        parsed.scheme == "https"
        and parsed.port in (None, 443)
        and any(host == allowed or host.endswith(f".{allowed}") for allowed in PUSH_HOSTS)
    )


def _decode(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def valid_keys(p256dh, auth):
    """Clé publique P-256 non compressée (65 octets) et secret de 16 octets, en base64 url."""
    try:
        public, secret = _decode(p256dh), _decode(auth)
    except (binascii.Error, ValueError):
        return False
    return len(public) == 65 and public[0] == 4 and len(secret) == 16


def subscribe(user, endpoint, p256dh, auth):
    """Enregistre l'abonnement d'un navigateur. Un même navigateur passé à un autre
    compte change de propriétaire ; au-delà de 10 appareils, le plus ancien s'en va."""
    subscription, _ = PushSubscription.objects.update_or_create(
        endpoint=endpoint, defaults={"user": user, "p256dh": p256dh, "auth": auth}
    )
    extra = PushSubscription.objects.filter(user=user).order_by("-created_at", "-pk")[MAX_DEVICES:]
    PushSubscription.objects.filter(pk__in=[old.pk for old in extra]).delete()
    return subscription


def _midnight(now):
    local = timezone.localtime(now)
    return timezone.make_aware(datetime.combine(local.date(), time.min))


def _payload(pending):
    if len(pending) == 1:
        notification = pending[0]
        title, body, url = notification.title, notification.body, notification.url or "/notifications"
    else:
        title = f"{len(pending)} nouveautés sur XiMaths"
        body = " · ".join(notification.title for notification in pending)
        url = "/notifications"
    if len(body) > BODY_MAX:
        body = f"{body[: BODY_MAX - 1]}…"
    return json.dumps({"title": title, "body": body, "url": url}, ensure_ascii=False)


def _send(subscription, payload, now):
    try:
        webpush(
            {"endpoint": subscription.endpoint, "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth}},
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_SUBJECT},
            ttl=TTL,
            timeout=TIMEOUT,
        )
    except WebPushException as error:
        status = error.response.status_code if error.response is not None else None
        if status in (404, 410):
            # Abonnement révoqué par le navigateur ou expiré.
            subscription.delete()
        else:
            logger.warning("Push refusé par %s : %s", urlparse(subscription.endpoint).hostname, status)
        return False
    except (requests.RequestException, ValueError) as error:
        logger.warning("Push impossible vers %s : %s", urlparse(subscription.endpoint).hostname, error)
        return False
    subscription.last_push_at = now
    subscription.save(update_fields=["last_push_at"])
    return True


def deliver(user, *, now=None):
    """Envoie les notifications en attente de `user` en un message, si c'est permis :
    push configuré, hors heures calmes, rien d'envoyé depuis minuit. Renvoie le nombre
    d'appareils atteints."""
    from .services import in_quiet_hours

    now = now or timezone.now()
    if not enabled() or not user.is_active or in_quiet_hours(now):
        return 0
    subscriptions = list(user.push_subscriptions.all())
    if not subscriptions or Notification.objects.filter(user=user, pushed_at__gte=_midnight(now)).exists():
        return 0
    pending = list(
        Notification.objects.filter(
            user=user, kind__in=PUSH_KINDS, read_at=None, pushed_at=None, created_at__gte=now - PENDING_WINDOW
        )
    )
    if not pending:
        return 0
    payload = _payload(pending)
    reached = sum(_send(subscription, payload, now) for subscription in subscriptions)
    # Aucun appareil atteint (réseau, service en panne) : on retentera dans l'heure.
    if reached:
        Notification.objects.filter(pk__in=[n.pk for n in pending]).update(pushed_at=now)
    return reached


def deliver_after_commit(user, *, now=None):
    """Appelé par notify : le push part une fois la transaction validée, et une erreur
    imprévue n'interrompt jamais l'action qui a créé la notification."""

    def send():
        try:
            deliver(user, now=now)
        except Exception:
            logger.exception("Push vers %s impossible", user.pk)

    if enabled():
        transaction.on_commit(send)


def send_pending_pushes(*, now=None):
    """Tâche horaire : les notifications retenues pendant les heures calmes, ou dont
    l'envoi a échoué. Renvoie le nombre de membres atteints."""
    from accounts.models import User

    if not enabled():
        return 0
    users = User.objects.filter(is_active=True, push_subscriptions__isnull=False).distinct()
    return sum(1 for user in users if deliver(user, now=now))
