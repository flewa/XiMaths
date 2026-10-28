from django.contrib import admin

from .models import Level, Topic


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "track", "year", "display_order")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    prepopulated_fields = {"slug": ("name",)}
