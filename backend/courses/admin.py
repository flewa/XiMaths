from django.contrib import admin

from . import services
from .models import CourseNote


@admin.register(CourseNote)
class CourseNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "cycle", "programs", "position", "topic", "published_at")
    list_filter = ("cycle", ("published_at", admin.EmptyFieldListFilter))
    search_fields = ("title", "body")
    readonly_fields = ("slug", "source_hash", "published_at", "published_by", "created_at", "updated_at")
    actions = ["publish", "unpublish"]

    @admin.action(description="Publier les fiches choisies")
    def publish(self, request, queryset):
        for note in queryset:
            services.publish(note, request.user)

    @admin.action(description="Repasser en brouillon")
    def unpublish(self, request, queryset):
        for note in queryset:
            services.unpublish(note)
