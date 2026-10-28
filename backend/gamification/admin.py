from django.contrib import admin

from .models import PointTransaction, UserBadge


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("awarded_at", "user", "badge")
    list_filter = ("badge",)
    search_fields = ("user__username",)


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    """Consultation seule : le ledger ne se corrige que par des annulations."""

    list_display = ("created_at", "user", "amount", "reason", "source_type", "source_id", "level")
    list_filter = ("reason", "level")
    search_fields = ("user__username",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
