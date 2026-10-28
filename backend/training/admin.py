from django.contrib import admin

from .models import TimedSession


@admin.register(TimedSession)
class TimedSessionAdmin(admin.ModelAdmin):
    """Consultation : les sessions évoluent par l'API, jamais à la main."""

    list_display = ("started_at", "user", "exercise", "status", "elapsed_s", "duration_s", "focus_losses", "answer_correct")
    list_filter = ("status", "answer_correct")
    search_fields = ("user__username", "exercise__title")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
