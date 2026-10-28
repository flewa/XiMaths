from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .links import link_accounts
from .models import AccountLink, User


@admin.register(AccountLink)
class AccountLinkAdmin(admin.ModelAdmin):
    """Comptes liés : détectés par la réciprocité des votes, ou ajoutés à la main.
    Un lien neutralise les interactions mutuelles ; ce n'est pas une sanction."""

    list_display = ("user_a", "user_b", "link_type", "strength", "confirmed_by", "created_at")
    list_filter = ("link_type",)
    search_fields = ("user_a__username", "user_b__username")
    autocomplete_fields = ("user_a", "user_b")
    fields = ("user_a", "user_b", "link_type", "strength")

    def has_change_permission(self, request, obj=None):
        return obj is None

    def save_model(self, request, obj, form, change):
        # Passe par link_accounts pour neutraliser aussi les votes mutuels passés.
        link, _ = link_accounts(
            obj.user_a, obj.user_b, obj.link_type, strength=obj.strength, confirmed_by=request.user
        )
        obj.pk = link.pk


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "declared_level", "trust_level", "status")
    list_filter = ("trust_level", "status", "verified_teacher", "declared_level")
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "XiMaths",
            {
                "fields": (
                    "declared_level",
                    "trust_level",
                    "status",
                    "verified_teacher",
                    "email_verified_at",
                    "academic_verified_at",
                    "academic_domain",
                    "leaderboard_visible",
                    "tiers_temps",
                )
            },
        ),
    )
