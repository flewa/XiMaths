import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver

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
    visitor_reads = models.PositiveIntegerField(
        default=0, help_text="Lectures de la page par des visiteurs non connectés, une par navigateur."
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
    variant_statement = models.TextField(
        "énoncé tiré",
        blank=True,
        help_text="Défi paramétré : l'énoncé avec les paramètres de l'auteur, montré aux relecteurs.",
    )
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
    review_round = models.PositiveSmallIntegerField(
        default=1, help_text="Tour de relecture : une révision importante en ouvre un nouveau."
    )
    recommended_at = models.DateTimeField(
        null=True, blank=True, help_text="Recommandée par l'auteur de l'exercice (une par exercice)."
    )
    # Copie modèle : l'auteur donne son accord, l'équipe choisit une copie validée par
    # exercice. Elle est montrée sans nom aux membres qui ont envoyé la leur.
    model_consent = models.BooleanField(default=False)
    model_at = models.DateTimeField(null=True, blank=True)
    # Envoyée (ou révisée) après que son auteur a ouvert la copie modèle : sans points.
    after_model = models.BooleanField(default=False)

    class Meta:
        ordering = ["-validated_at", "-published_at"]

    def __str__(self):
        return f"Solution {self.pk} de « {self.exercise} »"


class PhotoUpload(models.Model):
    """Envoi de photos de copie, souvent depuis un téléphone : le QR code affiché sur
    l'ordinateur porte le jeton, qui suffit pour déposer des photos pendant un temps
    limité, sans se connecter sur le téléphone (voir content/photos.py)."""

    token = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="photo_uploads"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Fin du dépôt de photos ; elles restent un jour à joindre.")

    def __str__(self):
        return f"Envoi de photos de {self.user} pour « {self.exercise} »"


def _photo_path(photo, filename):
    # Nom tiré au hasard : rien du nom d'origine ni de l'auteur.
    return f"copies/{uuid.uuid4().hex}.jpg"


class SolutionPhoto(models.Model):
    """Photo d'une page de copie manuscrite : déposée dans un envoi, puis jointe à la
    solution quand l'auteur l'envoie en relecture. Réencodée en JPEG, sans métadonnées."""

    upload = models.ForeignKey(
        PhotoUpload, null=True, blank=True, on_delete=models.SET_NULL, related_name="photos"
    )
    solution = models.ForeignKey(
        Solution, null=True, blank=True, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.FileField(upload_to=_photo_path)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    position = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "pk"]

    def __str__(self):
        return f"Photo {self.pk} ({self.width}×{self.height})"


@receiver(post_delete, sender=SolutionPhoto)
def _delete_photo_file(sender, instance, **kwargs):
    # Le fichier part avec la ligne : purge des envois expirés, révision, solution supprimée.
    instance.image.delete(save=False)


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
    round = models.PositiveSmallIntegerField(default=1, help_text="Tour de relecture de la solution.")
    reminded_at = models.DateTimeField(null=True, blank=True, help_text="Relance envoyée à 48 h.")
    expired_at = models.DateTimeField(
        null=True, blank=True, help_text="Non rendue à 72 h : réattribuée à un autre relecteur."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["solution", "reviewer"], name="review_unique_reviewer"
            ),
        ]


class ExerciseRead(models.Model):
    """Un membre a ouvert la page d'un exercice : une ligne par membre et par exercice. Sert
    aux statistiques de l'exercice (combien l'ont lu, combien ont envoyé une copie)."""

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exercise_reads")
    first_read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["exercise", "user"], name="exercise_read_once_per_member")]


class ModelCopyView(models.Model):
    """Un membre a ouvert la copie modèle d'un exercice : ses copies suivantes sur cet
    exercice ne rapportent plus de points."""

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="model_views")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="model_views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["exercise", "user"], name="model_copy_view_once_per_member")]


class Message(models.Model):
    """Question ou remarque sous un exercice. Les réponses n'ont qu'un niveau : on répond
    à un message, pas à une réponse. Retiré, un message garde sa place si on lui a
    répondu, sans son texte."""

    MAX_LENGTH = 2000

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="messages"
    )
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    body = models.TextField(max_length=MAX_LENGTH, help_text="Markdown et LaTeX.")
    created_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    # Retiré par l'équipe (et non par son auteur) : l'auteur en est prévenu.
    removed_by_team = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at", "pk"]
        indexes = [models.Index(fields=["exercise", "created_at"])]

    def __str__(self):
        return f"Message de {self.author} sous « {self.exercise} »"


class MessageFlag(models.Model):
    """Un membre signale un message à l'équipe : une fois par message."""

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="flags")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="message_flags")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["message", "user"], name="message_flag_once_per_member")]


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
