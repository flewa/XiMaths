"""Comptes : inscription, connexion par session Django, vérification de l'email.

Le front appelle ces routes via son proxy /api, donc sur la même origine : le
cookie de session suffit, et chaque écriture porte l'en-tête X-CSRFToken.
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.middleware.csrf import get_token
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth
from ninja.throttling import AnonRateThrottle, AuthRateThrottle
from ninja.utils import check_csrf
from pydantic import Field

from catalog.models import Level
from config.errors import RuleError
from content.models import Review, Solution
from gamification.services import balance

from .models import User
from .services import send_verification_email, verify_email

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

    @staticmethod
    def resolve_email_verified(obj):
        return obj.email_verified_at is not None

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
    tiers_temps: bool


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
    throttle=[AnonRateThrottle("20/h")],
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


@router.post("/login", response=MeOut, throttle=[AnonRateThrottle("10/m")])
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
    if user.status in (User.Status.SUSPENDED, User.Status.BANNED):
        raise HttpError(403, "Ce compte est suspendu.")
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
    throttle=[AuthRateThrottle("3/h")],
)
def resend_verification(request):
    if request.auth.email_verified_at is not None:
        raise HttpError(409, "Ton adresse email est déjà vérifiée.")
    send_verification_email(request.auth)
    return 204, None


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
    """Tiers-temps (×1,33), déclaré par l'utilisateur et appliqué à tous les modes
    chronométrés, à partir de la prochaine session."""
    user = request.auth
    user.tiers_temps = payload.tiers_temps
    user.save(update_fields=["tiers_temps"])
    return user
