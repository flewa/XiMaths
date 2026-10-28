from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.html import format_html

from config.errors import RuleError

from .models import Report
from .services import resolve_report

CONFIRM, REJECT = "confirme", "rejete"


class ReportDecisionForm(forms.ModelForm):
    decision = forms.ChoiceField(
        label="Décision",
        required=False,
        choices=[("", "—"), (CONFIRM, "Confirmer le signalement"), (REJECT, "Ne pas le retenir")],
    )
    motif = forms.CharField(
        label="Motif",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Obligatoire pour confirmer : il est communiqué à l'auteur du contenu.",
    )

    class Meta:
        model = Report
        fields = []

    def clean(self):
        data = super().clean()
        if data.get("decision") == CONFIRM and not data.get("motif", "").strip():
            self.add_error("motif", "Motive la décision.")
        return data


@admin.action(description="Ne pas retenir (sans suite)")
def reject(modeladmin, request, queryset):
    count = 0
    for report in queryset.filter(status=Report.Status.OPEN):
        try:
            resolve_report(report, confirmed=False, moderator=request.user, note="Signalement non retenu.")
            count += 1
        except (RuleError, PermissionDenied) as error:
            modeladmin.message_user(request, f"{report} : {error}", messages.ERROR)
    if count:
        modeladmin.message_user(request, f"{count} signalement(s) non retenu(s).", messages.SUCCESS)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """File des signalements. Les doublons se tranchent dans la file des doublons."""

    form = ReportDecisionForm
    list_display = ("created_at", "reason", "target_title", "reporter", "status")
    list_filter = ("status", "reason")
    search_fields = ("details", "exercise__title", "solution__exercise__title", "reporter__username")
    actions = [reject]
    readonly_fields = (
        "content",
        "reason",
        "details",
        "reporter",
        "pair_link",
        "status",
        "decided_by",
        "decided_at",
        "decision_note",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        fieldsets = [(None, {"fields": self.readonly_fields})]
        if obj and obj.status == Report.Status.OPEN and obj.reason != Report.Reason.DUPLICATE:
            fieldsets.append(("Décision", {"fields": ("decision", "motif")}))
        return fieldsets

    @admin.display(description="Contenu")
    def target_title(self, report):
        exercise = report.exercise or report.solution.exercise
        return exercise.title if report.exercise else f"Solution sur « {exercise.title} »"

    @admin.display(description="Contenu signalé")
    def content(self, report):
        exercise = report.exercise or report.solution.exercise
        body = report.exercise.statement if report.exercise else report.solution.body
        author = (report.exercise or report.solution).author
        return format_html(
            '<p><a href="{}" target="_blank">{}</a> · auteur : {}</p><pre style="white-space:pre-wrap">{}</pre>',
            f"{settings.FRONTEND_URL}/exercices/{exercise.pk}",
            self.target_title(report),
            author or "compte supprimé",
            body,
        )

    @admin.display(description="Paire de doublons")
    def pair_link(self, report):
        if report.duplicate_pair_id is None:
            return "—"
        url = reverse("admin:duplicates_duplicatepair_change", args=[report.duplicate_pair_id])
        return format_html('<a href="{}">{}</a> (à trancher dans la file des doublons)', url, report.duplicate_pair)

    def save_model(self, request, obj, form, change):
        # Rien d'autre n'est modifiable : la décision passe par le service, qui applique ses effets.
        decision = form.cleaned_data.get("decision")
        if not decision:
            return
        try:
            resolve_report(
                obj,
                confirmed=decision == CONFIRM,
                moderator=request.user,
                note=form.cleaned_data.get("motif", ""),
            )
        except (RuleError, PermissionDenied) as error:
            self.message_user(request, str(error), messages.ERROR)
