"""Connexion avec Google : OpenID Connect, flux « code d'autorisation ».

Configuration : GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET. L'adresse de retour à
déclarer chez Google est {FRONTEND_URL}/api/auth/google/callback : elle passe par
le proxy du front, pour que le cookie de session soit posé sur la bonne origine.
"""

import json
import secrets
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import jwt
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from config.errors import RuleError

from .models import User
from .services import available_username

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
ISSUERS = ["https://accounts.google.com", "accounts.google.com"]
STATE_SESSION_KEY = "google_oauth_state"

_jwks_client = None


def enabled():
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def redirect_uri():
    return f"{settings.FRONTEND_URL}/api/auth/google/callback"


def authorization_url(session, next_path="/"):
    """Adresse de connexion chez Google. Le jeton `state` protège contre la
    falsification de requêtes ; il retient aussi la page où revenir."""
    state = secrets.token_urlsafe(24)
    session[STATE_SESSION_KEY] = {"state": state, "next": next_path}
    query = urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri(),
            "response_type": "code",
            "scope": "openid email",
            "state": state,
            "prompt": "select_account",
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


def check_state(session, state):
    """Renvoie la page où revenir, ou lève RuleError si l'état ne correspond pas."""
    saved = session.pop(STATE_SESSION_KEY, None)
    if not saved or not state or not secrets.compare_digest(saved["state"], state):
        raise RuleError("La connexion avec Google a expiré : recommence.")
    return saved["next"]


def exchange_code(code):
    """Échange le code contre un jeton d'identité, et en renvoie les informations vérifiées."""
    request = Request(
        TOKEN_URL,
        data=urlencode(
            {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri(),
                "grant_type": "authorization_code",
            }
        ).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urlopen(request, timeout=10) as response:
        id_token = json.load(response)["id_token"]
    return verify_id_token(id_token)


def verify_id_token(id_token):
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(JWKS_URL)
    key = _jwks_client.get_signing_key_from_jwt(id_token)
    return jwt.decode(
        id_token,
        key.key,
        algorithms=["RS256"],
        audience=settings.GOOGLE_CLIENT_ID,
        issuer=ISSUERS,
    )


@transaction.atomic
def user_for_claims(claims):
    """Compte lié à ce compte Google : déjà lié, sinon celui qui a la même adresse
    vérifiée, sinon un nouveau compte, à l'adresse déjà vérifiée par Google."""
    if not claims.get("email_verified"):
        raise RuleError("Ton adresse Google n'est pas vérifiée.")
    subject, email = claims["sub"], claims["email"].lower()
    user = User.objects.filter(google_sub=subject).first()
    if user is None:
        user = User.objects.filter(email__iexact=email).first()
        if user is not None:
            user.google_sub = subject
    if user is None:
        user = User(username=available_username(email), email=email, google_sub=subject)
        user.set_unusable_password()
    if not user.is_active:
        raise RuleError("Ce compte est fermé.")
    if user.email_verified_at is None:
        user.email_verified_at = timezone.now()
    user.save()
    return user
