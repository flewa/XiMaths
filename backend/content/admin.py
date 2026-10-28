from django.contrib import admin

from .models import Exercise, Review, Solution, Vote


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


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ("pk", "exercise", "author", "status", "ai_usage", "origin", "published_at")
    list_filter = ("status", "ai_usage", "origin")
    search_fields = ("body", "exercise__title")
    inlines = [ReviewInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "exercise", "solution", "weight", "created_at")
