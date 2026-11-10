from django.conf import settings
from django.core.exceptions import PermissionDenied
from ninja import NinjaAPI

from accounts.api import router as auth_router
from content.api import router as content_router
from courses.api import router as courses_router
from gamification.api import router as progression_router
from moderation.api import router as moderation_router
from notifications.api import router as notifications_router
from training.api import router as training_router

from .errors import RuleError

# La documentation interactive sert au développement ; en production, elle ne sert à aucun
# visiteur et décrit toute l'API à qui la cherche.
api = NinjaAPI(
    title="XiMaths API",
    version="0.4.0",
    docs_url="/docs" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)
api.add_router("/auth", auth_router)
api.add_router("/", content_router)
api.add_router("/", progression_router)
api.add_router("/", moderation_router)
api.add_router("/", training_router)
api.add_router("/", notifications_router)
api.add_router("/", courses_router)


@api.exception_handler(PermissionDenied)
def permission_denied(request, exc):
    return api.create_response(
        request, {"detail": str(exc) or "Action non autorisée."}, status=403
    )


@api.exception_handler(RuleError)
def rule_error(request, exc):
    return api.create_response(request, {"detail": str(exc)}, status=409)


@api.get("/health")
def health(request):
    return {"status": "ok"}
