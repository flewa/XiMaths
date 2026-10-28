from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

TEXT_MAX_LENGTH = 20_000
# Nombre de notes de difficulté à partir duquel l'estimation remplace la déclaration.
MIN_DIFFICULTY_RATINGS = 5


class Exercise(models.Model):
    class SourceType(models.TextChoices):
        PERSONAL = "personnel", "Création personnelle"
        INSPIRED = "inspire", "Inspiré de"
        REPRODUCED = "reproduit", "Reproduit avec autorisation"

    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PUBLISHED = "published", "Publié"
        MERGED = "merged", "Fusionné"
        REMOVED = "removed", "Retiré"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="exercises",
    )
    title = models.CharField(max_length=200)
    statement = models.TextField(
        max_length=TEXT_MAX_LENGTH, help_text="Markdown et LaTeX."
    )
    hints = models.JSONField(
        default=list, blank=True, help_text="Indications progressives, dans l'ordre."
    )
    final_answer = models.CharField(
        max_length=500,
        blank=True,
        help_text="Réponse finale vérifiable par SymPy, pour les défis chronométrés.",
    )
    difficulty_declared = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    difficulty_estimated = models.FloatField(null=True, blank=True)
    difficulty_ratings = models.PositiveIntegerField(default=0)
    primary_level = models.ForeignKey(
        "catalog.Level", on_delete=models.PROTECT, related_name="primary_exercises"
    )
    levels = models.ManyToManyField(
        "catalog.Level", related_name="exercises", blank=True
    )
    topics = models.ManyToManyField(
        "catalog.Topic", related_name="exercises", blank=True
    )
    source_type = models.CharField(
        max_length=16, choices=SourceType.choices, default=SourceType.PERSONAL
    )
    source_reference = models.CharField(max_length=300, blank=True)
    license = models.CharField(max_length=32, default="CC-BY-SA-4.0")
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.DRAFT
    )
    feed_impressions = models.PositiveIntegerField(
        default=0, help_text="Affichages dans le fil d'accueil, pour l'exposition minimale."
    )
    merged_into = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="merged_exercises",
        help_text="Exercice canonique, après une fusion de doublons.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(difficulty_declared__gte=1, difficulty_declared__lte=5),
                name="exercise_difficulty_1_5",
            ),
            models.CheckConstraint(
                condition=Q(source_type="personnel") | ~Q(source_reference=""),
                name="exercise_source_reference_required",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def difficulty(self):
        """Difficulté retenue par le barème : l'estimation dès 5 notes, sinon la déclaration."""
        if (
            self.difficulty_estimated is not None
            and self.difficulty_ratings >= MIN_DIFFICULTY_RATINGS
        ):
            return min(5, max(1, round(self.difficulty_estimated)))
        return self.difficulty_declared


class Solution(models.Model):
    class AiUsage(models.TextChoices):
        NONE = "aucune", "Aucune"
        PROOFREADING = "relecture", "Relecture ou mise en forme"
        IDEA = "aide_idee", "Aide sur une idée"
        GENERATED = "generee", "Solution générée"

    class Origin(models.TextChoices):
        FREE = "libre", "Libre"
        TRAINING = "entrainement", "Entraînement chronométré"
        DAILY = "defi", "Défi du jour"
        EXAM = "epreuve", "Épreuve classée"

    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        UNDER_REVIEW = "under_review", "En relecture"
        CONTESTED = "contested", "Contestée"
        VALIDATED = "validated", "Validée"
        NEEDS_WORK = "needs_work", "À compléter"
        HIDDEN = "hidden", "Masquée"

    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="solutions"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="solutions",
    )
    body = models.TextField(max_length=TEXT_MAX_LENGTH, help_text="Markdown et LaTeX.")
    ai_usage = models.CharField(
        max_length=16, choices=AiUsage.choices, default=AiUsage.NONE
    )
    origin = models.CharField(
        max_length=16, choices=Origin.choices, default=Origin.FREE
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-validated_at", "-published_at"]

    def __str__(self):
        return f"Solution {self.pk} de « {self.exercise} »"


class Review(models.Model):
    """Relecture d'une solution par un pair, tiré au sort ou volontaire."""

    class Verdict(models.TextChoices):
        CORRECT = "correcte", "Correcte"
        GAPS = "lacunes", "Correcte avec lacunes"
        INCORRECT = "incorrecte", "Incorrecte"

    solution = models.ForeignKey(
        Solution, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    assigned = models.BooleanField(
        default=True, help_text="Tiré au sort par le système plutôt que spontané."
    )
    verdict = models.CharField(max_length=16, choices=Verdict.choices, blank=True)
    feedback = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    agrees_with_consensus = models.BooleanField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["solution", "reviewer"], name="review_unique_reviewer"
            ),
        ]


class Vote(models.Model):
    """Vote « utile », sur un exercice ou sur une solution. Il n'y a pas de vote négatif."""

    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    exercise = models.ForeignKey(
        Exercise, null=True, blank=True, on_delete=models.CASCADE, related_name="votes"
    )
    solution = models.ForeignKey(
        Solution, null=True, blank=True, on_delete=models.CASCADE, related_name="votes"
    )
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(exercise__isnull=False, solution__isnull=True)
                | Q(exercise__isnull=True, solution__isnull=False),
                name="vote_single_target",
            ),
            models.UniqueConstraint(
                fields=["voter", "exercise"],
                condition=Q(exercise__isnull=False),
                name="vote_unique_exercise",
            ),
            models.UniqueConstraint(
                fields=["voter", "solution"],
                condition=Q(solution__isnull=False),
                name="vote_unique_solution",
            ),
        ]

    @property
    def target(self):
        return self.exercise or self.solution
