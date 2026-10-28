import random

from django import forms
from django.contrib import admin
from django.utils.html import format_html

from content.models import Exercise

from . import challenges
from .models import Challenge, ChallengeTemplate, TimedSession


@admin.register(TimedSession)
class TimedSessionAdmin(admin.ModelAdmin):
    """Consultation : les sessions évoluent par l'API, jamais à la main."""

    list_display = ("started_at", "user", "exercise", "challenge", "status", "elapsed_s", "duration_s", "focus_losses", "answer_correct")
    list_filter = ("status", "answer_correct", "challenge__level")
    search_fields = ("user__username", "exercise__title")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ChallengeTemplateForm(forms.ModelForm):
    class Meta:
        model = ChallengeTemplate
        fields = ["exercise", "statement", "parameters", "answer", "active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exercise"].queryset = Exercise.objects.filter(status=Exercise.Status.PUBLISHED)

    def clean(self):
        data = super().clean()
        template = ChallengeTemplate(
            statement=data.get("statement", ""), parameters=data.get("parameters"), answer=data.get("answer", "")
        )
        for error in challenges.check_template(template):
            self.add_error(None, error)
        return data


@admin.register(ChallengeTemplate)
class ChallengeTemplateAdmin(admin.ModelAdmin):
    """Gabarits du défi du jour. Le niveau du défi est celui de l'exercice ; la
    difficulté de l'exercice fixe le barème, 20 × m(d)."""

    form = ChallengeTemplateForm
    list_display = ("exercise", "level", "active")
    list_filter = ("active", "exercise__primary_level")
    readonly_fields = ("example",)

    @admin.display(description="Niveau")
    def level(self, template):
        return template.exercise.primary_level

    @admin.display(description="Exemple de tirage")
    def example(self, template):
        if not template.pk:
            return "—"
        values = challenges.draw(template, random.Random(0))
        return format_html(
            "<p>Paramètres : {}</p><pre style='white-space:pre-wrap'>{}</pre><p>Réponse attendue : {}</p>",
            values,
            challenges.fill(template, values),
            challenges.expected_answer(template, values),
        )


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    """Défis ouverts chaque jour par la tâche horaire, un par niveau."""

    list_display = ("date", "level", "template", "opens_at", "closes_at")
    list_filter = ("level",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
