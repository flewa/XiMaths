"""Vérification de l'adresse email par lien signé."""

import hashlib

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.utils import timezone

from config.errors import RuleError

from .models import User

EMAIL_TOKEN_SALT = "ximaths.email-verification"
EMAIL_TOKEN_MAX_AGE = 3 * 24 * 3600  # 3 jours


def _email_digest(email):
    # Le lien ne contient qu'une empreinte de l'adresse, pas l'adresse elle-même.
    return hashlib.sha256(email.lower().encode()).hexdigest()[:16]


def email_verification_token(user):
    """Jeton signé, invalidé si l'adresse change entre l'envoi et le clic."""
    return signing.dumps(
        {"uid": user.pk, "email": _email_digest(user.email)}, salt=EMAIL_TOKEN_SALT
    )


def send_verification_email(user):
    link = f"{settings.FRONTEND_URL}/verifier-email?token={email_verification_token(user)}"
    send_mail(
        "Confirme ton adresse email XiMaths",
        f"Bonjour {user.username},\n\n"
        f"Pour confirmer ton adresse et pouvoir contribuer, ouvre ce lien :\n{link}\n\n"
        "Il est valable 3 jours.",
        None,
        [user.email],
    )


def verify_email(token, *, now=None):
    try:
        data = signing.loads(token, salt=EMAIL_TOKEN_SALT, max_age=EMAIL_TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        raise RuleError("Ce lien a expiré : demande un nouvel email de vérification.")
    except signing.BadSignature:
        raise RuleError("Ce lien de vérification n'est pas valide.")
    user = User.objects.filter(pk=data.get("uid")).first()
    if user is None or _email_digest(user.email) != data.get("email"):
        raise RuleError("Ce lien de vérification n'est pas valide.")
    if user.email_verified_at is None:
        user.email_verified_at = now or timezone.now()
        user.save(update_fields=["email_verified_at"])
    return user
