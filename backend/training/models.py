from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from content.models import Exercise, Solution


class TimedSession(models.Model):
    """Session d'entraînement chronométré, non classée.

    Le serveur fait foi : le temps écoulé (`elapsed_s`) ne compte que les intervalles
    où le navigateur a donné signe de vie, d'où l'arrêt du chrono si l'onglet se ferme.
    """

    class Status(models.TextChoices):
        RUNNING = "en_cours", "En cours"
        PAUSED = "en_pause", "En pause"
        SUBMITTED = "rendue", "Rendue"
        ABANDONED = "abandonnee", "Abandonnée"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="timed_sessions"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="timed_sessions")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RUNNING)
    duration_s = models.PositiveIntegerField(help_text="Durée choisie, avant tiers-temps.")
    extra_time_factor = models.FloatField(default=1.0, help_text="1,33 avec un tiers-temps.")
    started_at = models.DateTimeField(help_text="Heure du serveur.")
    last_tick_at = models.DateTimeField(
        null=True, blank=True, help_text="Dernier signe de vie compté ; vide en pause."
    )
    elapsed_s = models.FloatField(default=0)
    pauses_used = models.PositiveSmallIntegerField(default=0)
    focus_losses = models.PositiveIntegerField(default=0, help_text="Sorties d'onglet, jamais pénalisées.")
    external_paste_chars = models.PositiveIntegerField(default=0, help_text="Taille des collages externes.")
    draft = models.TextField(blank=True)
    final_answer = models.CharField(max_length=200, blank=True)
    answer_correct = models.BooleanField(null=True, blank=True)
    solution = models.OneToOneField(
        Solution, null=True, blank=True, on_delete=models.SET_NULL, related_name="timed_session"
    )
    self_rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "session chronométrée"
        verbose_name_plural = "sessions chronométrées"
        ordering = ["-started_at"]
        constraints = [
            # Une seule session ouverte par exercice : la relancer la reprend.
            models.UniqueConstraint(
                fields=["user", "exercise"],
                condition=Q(status__in=["en_cours", "en_pause"]),
                name="timed_session_one_open_per_exercise",
            ),
        ]

    def __str__(self):
        return f"{self.user} · {self.exercise} ({self.get_status_display()})"

    @property
    def limit_s(self):
        return self.duration_s * self.extra_time_factor

    @property
    def open(self):
        return self.status in (self.Status.RUNNING, self.Status.PAUSED)
