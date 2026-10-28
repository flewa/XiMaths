from django.core.exceptions import PermissionDenied
from ninja import NinjaAPI

from accounts.api import router as auth_router
from content.api import router as content_router
from gamification.api import router as progression_router
from moderation.api import router as moderation_router
from training.api import router as training_router

from .errors import RuleError

api = NinjaAPI(title="XiMaths API", version="0.3.0")
api.add_router("/auth", auth_router)
api.add_router("/", content_router)
api.add_router("/", progression_router)
api.add_router("/", moderation_router)
api.add_router("/", training_router)


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
