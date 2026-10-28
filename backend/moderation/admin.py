from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.html import format_html

from config.errors import RuleError

from . import comprehension
from .models import Appeal, ComprehensionQuestion, IntegritySignal, Report, Sanction
from .services import (
    APPEAL_RESPONSE,
    decide_appeal,
    decide_signal,
    evaluate_question,
    lift,
    resolve_report,
    sanction,
)

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


class SignalDecisionForm(forms.ModelForm):
    decision = forms.ChoiceField(
        label="Décision",
        required=False,
        choices=[("", "—"), (REJECT, "Lever : la solution part en relecture"), (CONFIRM, "Plagiat confirmé")],
    )
    motif = forms.CharField(
        label="Motif",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Obligatoire pour confirmer : il est communiqué à l'auteur, qui peut faire appel.",
    )

    class Meta:
        model = IntegritySignal
        fields = []

    def clean(self):
        data = super().clean()
        if data.get("decision") == CONFIRM and not data.get("motif", "").strip():
            self.add_error("motif", "Motive la décision.")
        return data


@admin.register(IntegritySignal)
class IntegritySignalAdmin(admin.ModelAdmin):
    """Solutions en vérification : jamais de sanction sur un signal seul, un humain tranche."""

    form = SignalDecisionForm
    list_display = ("created_at", "kind", "user", "value", "status")
    list_filter = ("status", "kind")
    search_fields = ("user__username",)
    readonly_fields = ("comparison", "kind", "user", "value", "author_answer", "status", "decided_by", "decided_at", "decision_note")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        fieldsets = [(None, {"fields": self.readonly_fields})]
        if obj and obj.status == IntegritySignal.Status.OPEN:
            fieldsets.append(("Décision", {"fields": ("decision", "motif")}))
        return fieldsets

    @admin.display(description="Solutions côte à côte")
    def comparison(self, signal):
        column = '<div style="flex:1;min-width:0"><strong>{}</strong><pre style="white-space:pre-wrap">{}</pre></div>'
        matched = signal.matched_solution
        return format_html(
            '<div style="display:flex;gap:2rem">' + column + column + "</div>",
            f"Nouvelle, de {signal.user}",
            signal.solution.body if signal.solution else "—",
            f"Antérieure, de {matched.author if matched else '—'}",
            matched.body if matched else "—",
        )

    def save_model(self, request, obj, form, change):
        decision = form.cleaned_data.get("decision")
        if not decision:
            return
        try:
            decide_signal(
                obj, confirmed=decision == CONFIRM, moderator=request.user, note=form.cleaned_data.get("motif", "")
            )
        except (RuleError, PermissionDenied) as error:
            self.message_user(request, str(error), messages.ERROR)


@admin.action(description="Lever la sanction")
def lift_sanctions(modeladmin, request, queryset):
    lifted = 0
    for decision in queryset.filter(lifted_at=None):
        lift(decision, reason=f"Levée par {request.user}.")
        lifted += 1
    modeladmin.message_user(request, f"{lifted} sanction(s) levée(s).", messages.SUCCESS)


@admin.register(Sanction)
class SanctionAdmin(admin.ModelAdmin):
    """Sanctions : toujours humaines et motivées, notifiées au membre, qui peut faire appel."""

    list_display = ("created_at", "user", "kind", "ends_at", "lifted_at")
    list_filter = ("kind",)
    search_fields = ("user__username", "reason")
    raw_id_fields = ("user", "report")
    actions = [lift_sanctions]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("user", "kind", "reason", "report")
        return ("user", "kind", "reason", "report", "starts_at", "ends_at", "decided_by", "lifted_at", "lifted_reason")

    def get_readonly_fields(self, request, obj=None):
        return () if obj is None else self.get_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if change:
            return
        # Le service fixe la durée, met à jour le statut du compte et notifie le membre.
        decision = sanction(obj.user, obj.kind, reason=obj.reason, moderator=request.user, report=obj.report)
        obj.pk = decision.pk


class AppealDecisionForm(forms.ModelForm):
    decision = forms.ChoiceField(
        label="Décision",
        required=False,
        choices=[("", "—"), (REJECT, "Maintenir la décision"), (CONFIRM, "Annuler la décision")],
    )
    motif = forms.CharField(
        label="Motif",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Obligatoire : il est communiqué au membre.",
    )

    class Meta:
        model = Appeal
        fields = []

    def clean(self):
        data = super().clean()
        if data.get("decision") and not data.get("motif", "").strip():
            self.add_error("motif", "Motive la décision.")
        return data


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    """Appels : examinés par un autre modérateur que l'auteur de la décision, sous 7 jours."""

    form = AppealDecisionForm
    list_display = ("created_at", "user", "decision_summary", "status", "answer_by")
    list_filter = ("status",)
    search_fields = ("user__username", "statement")
    readonly_fields = ("user", "decision_summary", "statement", "created_at", "status", "decided_by", "decided_at", "decision_note")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        fieldsets = [(None, {"fields": self.readonly_fields})]
        if obj and obj.status == Appeal.Status.PENDING:
            fieldsets.append(("Décision", {"fields": ("decision", "motif")}))
        return fieldsets

    @admin.display(description="Décision contestée")
    def decision_summary(self, appeal):
        decision = appeal.decision
        if isinstance(decision, Sanction):
            return f"{decision.get_kind_display()} — {decision.reason}"
        if isinstance(decision, Report):
            return f"Retrait ({decision.get_reason_display()}) : {decision.target} — {decision.decision_note}"
        return f"Plagiat confirmé — {decision.decision_note}"

    @admin.display(description="Réponse attendue avant")
    def answer_by(self, appeal):
        return appeal.created_at + APPEAL_RESPONSE if appeal.status == Appeal.Status.PENDING else "—"

    def save_model(self, request, obj, form, change):
        decision = form.cleaned_data.get("decision")
        if not decision:
            return
        try:
            decide_appeal(obj, overturn=decision == CONFIRM, moderator=request.user, note=form.cleaned_data["motif"])
        except (RuleError, PermissionDenied) as error:
            self.message_user(request, str(error), messages.ERROR)


class ComprehensionQuestionForm(forms.ModelForm):
    decision = forms.ChoiceField(
        label="Évaluation",
        required=False,
        choices=[("", "—"), (CONFIRM, "Réussie : les points sont accordés"), (REJECT, "Insuffisante")],
    )
    motif = forms.CharField(label="Motif", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = ComprehensionQuestion
        fields = ["question", "expected_points"]


@admin.register(ComprehensionQuestion)
class ComprehensionQuestionAdmin(admin.ModelAdmin):
    """Sans LLM, un modérateur rédige la question sous 72 h ; l'enregistrer l'envoie au
    membre. Une réponse s'évalue ici ou depuis la page des arbitrages."""

    form = ComprehensionQuestionForm
    list_display = ("created_at", "user", "status", "integrity_score", "llm_assessment")
    list_filter = ("status", "llm_assessment")
    search_fields = ("user__username",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        context = ("solution_display", "integrity_score", "status", "sent_at", "opened_at", "answered_at")
        if obj and obj.status == ComprehensionQuestion.Status.TO_WRITE:
            return [(None, {"fields": context}), ("Question à rédiger", {"fields": ("question", "expected_points")})]
        fieldsets = [(None, {"fields": (*context, "question_display", "answer", "llm_assessment", "llm_rationale")})]
        if obj and obj.status == ComprehensionQuestion.Status.ANSWERED:
            fieldsets.append(("Évaluation", {"fields": ("decision", "motif")}))
        else:
            fieldsets.append(("Évaluation", {"fields": ("evaluated_by", "evaluated_at", "evaluation_note")}))
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly = ["solution_display", "integrity_score", "status", "sent_at", "opened_at", "answered_at", "question_display",
                    "answer", "llm_assessment", "llm_rationale", "evaluated_by", "evaluated_at", "evaluation_note"]
        return readonly

    @admin.display(description="Solution")
    def solution_display(self, question):
        solution = question.solution
        return format_html(
            "<p>{}</p><pre style='white-space:pre-wrap'>{}</pre><hr><pre style='white-space:pre-wrap'>{}</pre>",
            solution.exercise.title,
            solution.variant_statement or solution.exercise.statement,
            solution.body,
        )

    @admin.display(description="Question")
    def question_display(self, question):
        return question.question

    def save_model(self, request, obj, form, change):
        if obj.status == ComprehensionQuestion.Status.TO_WRITE:
            if obj.question.strip():
                comprehension.send(obj)
            return
        decision = form.cleaned_data.get("decision")
        if not decision:
            return
        try:
            evaluate_question(obj, passed=decision == CONFIRM, evaluator=request.user, note=form.cleaned_data.get("motif", ""))
        except (RuleError, PermissionDenied) as error:
            self.message_user(request, str(error), messages.ERROR)
