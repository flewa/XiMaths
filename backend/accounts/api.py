"""Comptes : inscription, connexion par session Django, vérification de l'email.

Le front appelle ces routes via son proxy /api, donc sur la même origine : le
cookie de session suffit, et chaque écriture porte l'en-tête X-CSRFToken.
"""

import json
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.utils.http import url_has_allowed_host_and_scheme
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth
from ninja.utils import check_csrf
from pydantic import Field

from catalog.models import Level
from config.errors import RuleError
from config.throttles import AnonRouteThrottle, AuthRouteThrottle
from content.models import Review, Solution
from gamification.services import balance

from . import academic, google
from .models import User
from .services import (
    delete_account,
    export_user_data,
    reset_password,
    send_password_reset,
    send_verification_email,
    set_password,
    verify_email,
)

router = Router(tags=["comptes"])


class MeOut(Schema):
    id: int
    username: str
    email: str
    email_verified: bool
    declared_level: str | None
    trust_level: int
    points: int
    pending_reviews: int
    leaderboard_visible: bool
    tiers_temps: bool
    email_notifications: bool
    weekly_digest: bool
    daily_challenge_notifications: bool
    has_password: bool
    google_linked: bool
    unread_notifications: int
    academic_verified_at: datetime | None
    # Domaine de l'adresse académique vérifiée ; l'adresse elle-même n'est pas gardée.
    academic_domain: str

    @staticmethod
    def resolve_email_verified(obj):
        return obj.email_verified_at is not None

    @staticmethod
    def resolve_has_password(obj):
        # Un compte créé avec Google n'a pas de mot de passe, tant qu'il n'en choisit pas.
        return obj.has_usable_password()

    @staticmethod
    def resolve_google_linked(obj):
        return bool(obj.google_sub)

    @staticmethod
    def resolve_unread_notifications(obj):
        return obj.notifications.filter(read_at=None).count()

    @staticmethod
    def resolve_declared_level(obj):
        return obj.declared_level.code if obj.declared_level else None

    @staticmethod
    def resolve_points(obj):
        return balance(obj)

    @staticmethod
    def resolve_pending_reviews(obj):
        return Review.objects.filter(
            reviewer=obj,
            submitted_at=None,
            expired_at=None,
            round=F("solution__review_round"),
            solution__status=Solution.Status.UNDER_REVIEW,
        ).count()


class SignupIn(Schema):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[\w.-]+$")
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)
    declared_level: str | None = None


class LoginIn(Schema):
    login: str = Field(description="Pseudo ou adresse email.")
    password: str


class TokenIn(Schema):
    token: str


class VisibilityIn(Schema):
    visible: bool


class PreferencesIn(Schema):
    """Seuls les champs envoyés changent."""

    declared_level: str | None = Field(None, description="Code du niveau ; chaîne vide pour aucun.")
    tiers_temps: bool | None = None
    leaderboard_visible: bool | None = None
    email_notifications: bool | None = None
    weekly_digest: bool | None = None
    daily_challenge_notifications: bool | None = None


class EmailIn(Schema):
    email: str = Field(max_length=254)


class ResetIn(Schema):
    uid: str = Field(max_length=64)
    token: str = Field(max_length=128)
    password: str = Field(min_length=8, max_length=128)


class PasswordIn(Schema):
    current_password: str = Field(default="", max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class DeleteIn(Schema):
    confirmation: str = Field(description="« SUPPRIMER », en toutes lettres.")
    password: str = Field(default="", max_length=128)


def require_csrf(request):
    """Les routes sans session (inscription, connexion) vérifient le CSRF elles-mêmes."""
    if check_csrf(request):
        raise HttpError(403, "Jeton CSRF manquant ou invalide : recharge la page.")


@router.get("/csrf")
def csrf(request):
    """Pose le cookie csrftoken, que le front renvoie dans l'en-tête X-CSRFToken."""
    return {"csrf_token": get_token(request)}


@router.post(
    "/signup",
    response={201: MeOut},
    throttle=[AnonRouteThrottle("inscription", "20/h")],
)
def signup(request, payload: SignupIn):
    require_csrf(request)
    email = payload.email.strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        raise HttpError(422, "Cette adresse email n'est pas valide.")
    if User.objects.filter(username__iexact=payload.username).exists():
        raise HttpError(409, "Ce pseudo est déjà pris.")
    if User.objects.filter(email__iexact=email).exists():
        raise HttpError(409, "Un compte existe déjà avec cette adresse email.")
    level = None
    if payload.declared_level:
        level = Level.objects.filter(code=payload.declared_level).first()
        if level is None:
            raise HttpError(422, "Niveau inconnu.")

    user = User(username=payload.username, email=email, declared_level=level)
    try:
        validate_password(payload.password, user)
    except ValidationError as error:
        raise HttpError(422, " ".join(error.messages))
    user.set_password(payload.password)
    user.save()

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    send_verification_email(user)
    return 201, user


@router.post("/login", response=MeOut, throttle=[AnonRouteThrottle("connexion", "10/m")])
def login_view(request, payload: LoginIn):
    require_csrf(request)
    identifier = payload.login.strip()
    account = User.objects.filter(
        Q(username__iexact=identifier) | Q(email__iexact=identifier)
    ).first()
    user = account and authenticate(
        request, username=account.username, password=payload.password
    )
    if not user:
        raise HttpError(401, "Pseudo, email ou mot de passe incorrect.")
    # Un compte suspendu se connecte encore, pour lire la décision et faire appel ;
    # contributor() lui refuse toute contribution.
    login(request, user)
    return user


@router.post("/logout", response={204: None}, auth=django_auth)
def logout_view(request):
    logout(request)
    return 204, None


@router.get("/me", response=MeOut, auth=django_auth)
def me(request):
    return request.auth


@router.post("/verify-email", response=MeOut)
def verify_email_view(request, payload: TokenIn):
    require_csrf(request)
    try:
        return verify_email(payload.token)
    except RuleError as error:
        raise HttpError(400, str(error))


@router.post(
    "/resend-verification",
    response={204: None},
    auth=django_auth,
    throttle=[AuthRouteThrottle("verification", "3/h")],
)
def resend_verification(request):
    if request.auth.email_verified_at is not None:
        raise HttpError(409, "Ton adresse email est déjà vérifiée.")
    send_verification_email(request.auth)
    return 204, None


@router.post(
    "/academic",
    response={204: None},
    auth=django_auth,
    throttle=[AuthRouteThrottle("email-academique", "5/h")],
)
def academic_email(request, payload: EmailIn):
    """Envoie un lien à une adresse académique : une fois confirmée, elle donne le
    badge « Étudiant vérifié ». Seuls son domaine et son empreinte sont gardés."""
    try:
        academic.send_academic_link(request.auth, payload.email)
    except RuleError as error:
        raise HttpError(422, str(error))
    return 204, None


@router.post("/academic/verify", response=MeOut)
def verify_academic(request, payload: TokenIn):
    require_csrf(request)
    try:
        return academic.verify_academic(payload.token)
    except RuleError as error:
        raise HttpError(400, str(error))


@router.post("/leaderboard-visibility", response=MeOut, auth=django_auth)
def set_leaderboard_visibility(request, payload: VisibilityIn):
    """Masque ou réaffiche sa présence dans les classements. Masqué, on n'y apparaît
    plus et les points ne sont plus affichés sur le profil public."""
    user = request.auth
    user.leaderboard_visible = payload.visible
    user.save(update_fields=["leaderboard_visible"])
    return user


@router.post("/preferences", response=MeOut, auth=django_auth)
def set_preferences(request, payload: PreferencesIn):
    """Réglages du compte. Le tiers-temps (×1,33) s'applique à tous les modes
    chronométrés, à partir de la prochaine session."""
    user = request.auth
    changes = payload.dict(exclude_unset=True)
    if "declared_level" in changes:
        code = changes.pop("declared_level") or None
        level = Level.objects.filter(code=code).first() if code else None
        if code and level is None:
            raise HttpError(422, "Niveau inconnu.")
        user.declared_level = level
    for field, value in changes.items():
        if value is not None:
            setattr(user, field, value)
    user.save()
    return user


@router.post(
    "/password-reset",
    response={204: None},
    throttle=[AnonRouteThrottle("mot-de-passe-oublie", "5/h")],
)
def password_reset(request, payload: EmailIn):
    """Envoie un lien de réinitialisation. Répond pareil que l'adresse existe ou non."""
    require_csrf(request)
    send_password_reset(payload.email)
    return 204, None


@router.post(
    "/password-reset/confirm",
    response={204: None},
    throttle=[AnonRouteThrottle("nouveau-mot-de-passe", "10/h")],
)
def password_reset_confirm(request, payload: ResetIn):
    require_csrf(request)
    try:
        reset_password(payload.uid, payload.token, payload.password)
    except RuleError as error:
        raise HttpError(400, str(error))
    return 204, None


@router.post(
    "/password",
    response={204: None},
    auth=django_auth,
    throttle=[AuthRouteThrottle("mot-de-passe", "10/h")],
)
def change_password(request, payload: PasswordIn):
    """Change le mot de passe ; un compte créé avec Google en choisit un sans l'ancien."""
    user = request.auth
    if user.has_usable_password() and not user.check_password(payload.current_password):
        raise HttpError(403, "Mot de passe actuel incorrect.")
    try:
        set_password(user, payload.new_password)
    except RuleError as error:
        raise HttpError(422, str(error))
    update_session_auth_hash(request, user)
    return 204, None


@router.get("/export", auth=django_auth)
def export(request):
    """Toutes tes données, en JSON (droit d'accès et de portabilité)."""
    response = HttpResponse(
        json.dumps(export_user_data(request.auth), ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="ximaths-mes-donnees.json"'
    return response


@router.post("/delete", response={204: None}, auth=django_auth)
def delete(request, payload: DeleteIn):
    """Supprime le compte : données personnelles effacées, contributions anonymisées."""
    user = request.auth
    if payload.confirmation.strip() != "SUPPRIMER":
        raise HttpError(422, "Écris SUPPRIMER pour confirmer.")
    if user.has_usable_password() and not user.check_password(payload.password):
        raise HttpError(403, "Mot de passe incorrect.")
    logout(request)
    delete_account(user)
    return 204, None


@router.get("/providers")
def providers(request):
    """Moyens de connexion proposés par le front."""
    return {"google": google.enabled()}


def _front(path):
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}{path}")


@router.get("/google/start")
def google_start(request, next: str = "/"):
    if not google.enabled():
        raise HttpError(404, "Connexion avec Google non configurée.")
    if not url_has_allowed_host_and_scheme(next, allowed_hosts=None) or not next.startswith("/"):
        next = "/"
    return HttpResponseRedirect(google.authorization_url(request.session, next))


@router.get("/google/callback")
def google_callback(request, code: str = "", state: str = ""):
    """Retour de Google : ouvre la session, puis renvoie vers la page de départ."""
    try:
        next_path = google.check_state(request.session, state)
        if not code:
            raise RuleError("Connexion avec Google annulée.")
        user = google.user_for_claims(google.exchange_code(code))
    except Exception:
        # État périmé, réseau ou jeton invalide : même issue, sans détail technique.
        return _front("/connexion?erreur=google")
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return _front(next_path)
