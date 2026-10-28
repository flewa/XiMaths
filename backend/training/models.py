from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from catalog.models import Level
from content.models import Exercise, Solution

# Tiers-temps, appliqué à tous les modes chronométrés.
EXTRA_TIME_FACTOR = 1.33


class ChallengeTemplate(models.Model):
    """Gabarit de défi : un exercice publié dont l'énoncé et la réponse dépendent de
    paramètres tirés pour chaque membre. Partager sa réponse ne sert donc à rien."""

    exercise = models.OneToOneField(
        Exercise, on_delete=models.CASCADE, related_name="challenge_template", verbose_name="exercice"
    )
    statement = models.TextField(
        "énoncé paramétré", help_text="Markdown et LaTeX ; {{a}} est remplacé par la valeur tirée pour a."
    )
    parameters = models.JSONField(
        "paramètres",
        help_text='Valeurs possibles de chaque paramètre, une lettre chacun : {"a": [2, 3, 4], "b": [2, 3, 5]}.',
    )
    answer = models.CharField(
        "réponse",
        max_length=200,
        help_text="Réponse en fonction des paramètres, vérifiée par SymPy : « b », « sqrt(a)/b »…",
    )
    active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "gabarit de défi"
        verbose_name_plural = "gabarits de défi"

    def __str__(self):
        return f"Gabarit : {self.exercise.title}"


class Challenge(models.Model):
    """Défi du jour d'un niveau : fenêtre de 24 h, 30 minutes, une seule tentative."""

    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="challenges", verbose_name="niveau")
    date = models.DateField()
    template = models.ForeignKey(ChallengeTemplate, on_delete=models.PROTECT, related_name="challenges")
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()

    class Meta:
        verbose_name = "défi du jour"
        verbose_name_plural = "défis du jour"
        ordering = ["-date", "level__display_order"]
        constraints = [models.UniqueConstraint(fields=["level", "date"], name="challenge_one_per_level_and_day")]

    def __str__(self):
        return f"Défi {self.level} du {self.date:%d/%m/%Y}"


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
    # Défi du jour : paramètres tirés, indications ouvertes, points accordés.
    challenge = models.ForeignKey(
        Challenge, null=True, blank=True, on_delete=models.CASCADE, related_name="sessions"
    )
    parameters = models.JSONField(default=dict, blank=True)
    hints_opened = models.PositiveSmallIntegerField(default=0)
    bonus = models.FloatField(null=True, blank=True, help_text="Bonus de rapidité, indications déduites.")
    answer_points = models.PositiveIntegerField(default=0)
    justification_points = models.PositiveIntegerField(
        default=0, help_text="Accordés quand la justification est validée par les pairs."
    )

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
            # Une seule tentative par défi ; abandonner la consomme.
            models.UniqueConstraint(
                fields=["user", "challenge"],
                condition=Q(challenge__isnull=False),
                name="timed_session_one_attempt_per_challenge",
            ),
        ]

    def __str__(self):
        return f"{self.user} · {self.exercise} ({self.get_status_display()})"

    @property
    def limit_s(self):
        return self.duration_s * self.extra_time_factor

    @property
    def ranked(self):
        """Défi classé : le chrono ne s'arrête pas, ni pause ni collage externe."""
        return self.challenge_id is not None

    @property
    def open(self):
        return self.status in (self.Status.RUNNING, self.Status.PAUSED)
