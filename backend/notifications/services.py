"""Notifications : dans l'application toujours, par email seulement pour ce qui
concerne directement le membre, hors heures calmes, et en résumé hebdomadaire sur opt-in.
"""

from datetime import time, timedelta

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMessage
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import DigestLog, Notification

Kind = Notification.Kind

# Emails envoyés tout de suite (hors heures calmes) : ce qui engage le membre.
IMMEDIATE_EMAIL = {
    Kind.CONTENT_REMOVED,
    Kind.SANCTION,
    Kind.APPEAL_DECIDED,
    Kind.SOLUTION_HELD,
    Kind.COMPREHENSION_QUESTION,
}
QUIET_START, QUIET_END = time(22, 0), time(8, 0)
RETENTION = timedelta(days=183)
UNSUBSCRIBE_SALT = "ximaths.unsubscribe"


def notify(user, kind, title, body="", url="", *, email=None, now=None):
    """Crée la notification, et l'email si le type l'exige et que le membre l'accepte."""
    if user is None or not user.is_active:
        return None
    wants_email = kind in IMMEDIATE_EMAIL if email is None else email
    notification = Notification.objects.create(
        user=user,
        kind=kind,
        title=title,
        body=body,
        url=url,
        email_pending=wants_email and user.email_notifications,
    )
    if notification.email_pending and not in_quiet_hours(now):
        _send(notification, now=now)
    return notification


def in_quiet_hours(now=None):
    local = timezone.localtime(now).time()
    return local >= QUIET_START or local < QUIET_END


def unsubscribe_token(user):
    return signing.dumps({"uid": user.pk}, salt=UNSUBSCRIBE_SALT)


def unsubscribe_url(user):
    return f"{settings.FRONTEND_URL}/api/notifications/unsubscribe?token={unsubscribe_token(user)}"


def unsubscribe(token):
    """Désabonnement en un clic, sans connexion : plus aucun email."""
    from accounts.models import User

    try:
        data = signing.loads(token, salt=UNSUBSCRIBE_SALT)
    except signing.BadSignature:
        return None
    user = User.objects.filter(pk=data.get("uid")).first()
    if user is not None:
        user.email_notifications = False
        user.weekly_digest = False
        user.save(update_fields=["email_notifications", "weekly_digest"])
    return user


def _mail(user, subject, text):
    link = unsubscribe_url(user)
    message = EmailMessage(
        subject,
        f"{text}\n\n—\nNe plus recevoir d'emails de XiMaths : {link}",
        None,
        [user.email],
        headers={"List-Unsubscribe": f"<{link}>", "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"},
    )
    message.send()


def _send(notification, *, now=None):
    user = notification.user
    link = f"\n\n{settings.FRONTEND_URL}{notification.url}" if notification.url else ""
    _mail(user, notification.title, f"{notification.body}{link}".strip())
    notification.email_pending = False
    notification.emailed_at = now or timezone.now()
    notification.save(update_fields=["email_pending", "emailed_at"])


def send_pending_emails(*, now=None):
    """Envoie les emails retenus pendant les heures calmes. Renvoie leur nombre."""
    if in_quiet_hours(now):
        return 0
    pending = Notification.objects.filter(email_pending=True).select_related("user")
    count = 0
    for notification in pending:
        if notification.user.email_notifications and notification.user.is_active:
            _send(notification, now=now)
            count += 1
        else:
            notification.email_pending = False
            notification.save(update_fields=["email_pending"])
    return count


def send_digests(*, now=None):
    """Résumé de la semaine écoulée, une fois par semaine, à ceux qui l'ont demandé."""
    from accounts.models import User

    now = now or timezone.now()
    iso = timezone.localtime(now).isocalendar()
    week = f"{iso.year}-W{iso.week:02d}"
    sent = 0
    for user in User.objects.filter(weekly_digest=True, is_active=True):
        recent = list(Notification.objects.filter(user=user, created_at__gte=now - timedelta(days=7))[:20])
        if not recent:
            continue
        try:
            with transaction.atomic():
                DigestLog.objects.create(user=user, week=week)
        except IntegrityError:
            continue  # déjà envoyé cette semaine
        lines = "\n".join(f"[+] {n.title}" + (f" — {settings.FRONTEND_URL}{n.url}" if n.url else "") for n in recent)
        _mail(user, "Ta semaine sur XiMaths", f"Bonjour {user.username},\n\nCette semaine :\n{lines}")
        sent += 1
    return sent


def purge_old(*, now=None):
    """Les notifications sont gardées 6 mois."""
    return Notification.objects.filter(created_at__lt=(now or timezone.now()) - RETENTION).delete()[0]
