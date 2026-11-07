from django.contrib import admin
from django.utils.html import format_html

from . import photos
from .models import Exercise, Review, Solution, SolutionPhoto, Vote


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "primary_level", "difficulty_declared", "status", "published_at")
    list_filter = ("status", "primary_level", "source_type")
    search_fields = ("title", "statement")
    filter_horizontal = ("levels", "topics")


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ("weight", "agrees_with_consensus", "assigned_at", "submitted_at")


class PhotoInline(admin.TabularInline):
    """Photos de la copie, en vignettes : un clic ouvre la photo entière."""

    model = SolutionPhoto
    extra = 0
    fields = ("preview", "width", "height", "position")
    readonly_fields = fields
    can_delete = False

    @admin.display(description="photo")
    def preview(self, photo):
        url = photos.photo_url(photo)
        return format_html('<a href="{}" target="_blank" rel="noopener"><img src="{}" alt="" style="height:120px"></a>', url, url)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ("pk", "exercise", "author", "status", "ai_usage", "origin", "published_at")
    list_filter = ("status", "ai_usage", "origin")
    search_fields = ("body", "exercise__title")
    inlines = [PhotoInline, ReviewInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "exercise", "solution", "weight", "created_at")
