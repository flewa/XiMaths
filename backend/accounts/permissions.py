from ninja.errors import HttpError

from .models import User


def is_moderator(user):
    """Modérateur nommé, ou membre de l'équipe (accès à l'admin)."""
    return user.is_staff or user.trust_level >= User.TrustLevel.MODERATOR


def contributor(request):
    """L'utilisateur connecté, s'il peut contribuer : compte actif et adresse email vérifiée."""
    user = request.auth
    if user.status != User.Status.ACTIVE:
        raise HttpError(403, "Ton compte ne peut pas contribuer pour le moment.")
    if user.email_verified_at is None:
        raise HttpError(403, "Vérifie ton adresse email pour contribuer.")
    return user
