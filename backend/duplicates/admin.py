from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html

from config.errors import RuleError

from .models import DuplicatePair
from .services import decide, unmerge

Status = DuplicatePair.Status


def _apply(modeladmin, request, queryset, action, done):
    count = 0
    for pair in queryset.select_related("exercise", "existing"):
        try:
            action(pair)
            count += 1
        except (RuleError, PermissionDenied) as error:
            modeladmin.message_user(request, f"{pair} : {error}", messages.ERROR)
    if count:
        modeladmin.message_user(request, f"{count} paire(s) {done}.", messages.SUCCESS)


@admin.action(description="Fusionner : le plus récent rejoint le plus ancien")
def merge(modeladmin, request, queryset):
    _apply(modeladmin, request, queryset, lambda p: decide(p, Status.MERGED, request.user), "fusionnée(s)")


@admin.action(description="Lier comme variantes")
def link_as_variants(modeladmin, request, queryset):
    _apply(modeladmin, request, queryset, lambda p: decide(p, Status.VARIANTS, request.user), "liée(s)")


@admin.action(description="Déclarer distincts (ne sera plus reproposé)")
def declare_distinct(modeladmin, request, queryset):
    _apply(modeladmin, request, queryset, lambda p: decide(p, Status.DISTINCT, request.user), "déclarée(s) distincte(s)")


@admin.action(description="Annuler la fusion")
def cancel_merge(modeladmin, request, queryset):
    _apply(modeladmin, request, queryset, lambda p: unmerge(p, request.user), "défusionnée(s)")


@admin.register(DuplicatePair)
class DuplicatePairAdmin(admin.ModelAdmin):
    """File « Doublons à arbitrer », triée par score décroissant."""

    list_display = ("exercise", "existing", "band", "score_display", "author_choice", "author_note", "status", "created_at")
    list_filter = ("status", "band", "author_choice")
    search_fields = ("exercise__title", "existing__title", "author_note")
    actions = [merge, link_as_variants, declare_distinct, cancel_merge]
    readonly_fields = (
        "comparison", "exercise", "existing", "band", "score", "jaccard", "abstract_jaccard",
        "cosine", "author_choice", "author_note", "status", "decided_by", "decided_at",
        "moved_solutions", "created_at",
    )
    fields = readonly_fields

    # Les paires naissent de la publication ou du scan, et restent comme trace des décisions.
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="s / J(F)")
    def score_display(self, pair):
        score = "—" if pair.score is None else f"{pair.score:.2f}"
        return f"{score} / {pair.jaccard:.2f}"

    @admin.display(description="Énoncés côte à côte")
    def comparison(self, pair):
        column = '<div style="flex:1;min-width:0"><strong>{}</strong><pre style="white-space:pre-wrap">{}</pre></div>'
        return format_html(
            '<div style="display:flex;gap:2rem">' + column + column + "</div>",
            f"Nouveau : {pair.exercise.title}",
            pair.exercise.statement,
            f"Existant : {pair.existing.title}",
            pair.existing.statement,
        )
