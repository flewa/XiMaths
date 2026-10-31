from django.contrib import admin

from .models import Notification, PushSubscription


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "kind", "title", "read_at", "emailed_at", "pushed_at")
    list_filter = ("kind",)
    search_fields = ("user__username", "title")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "last_push_at")
    search_fields = ("user__username",)
    readonly_fields = ("user", "endpoint", "p256dh", "auth", "created_at", "last_push_at")

    def has_add_permission(self, request):
        return False
