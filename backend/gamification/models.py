from django.conf import settings
from django.db import models
from django.utils import timezone


class PointTransaction(models.Model):
    """Écriture du grand livre des points.

    Le ledger est en ajout seul : on n'y modifie ni ne supprime rien, on annule
    une écriture par une écriture opposée (`reverses`). Les classements se
    reconstruisent en sommant les montants.
    """

    class Reason(models.TextChoices):
        EXERCISE_PUBLISHED = "exercise_published", "Exercice publié"
        EXERCISE_SOLVED = "exercise_solved", "Solution validée reçue sur son exercice"
        EXERCISE_UPVOTED = "exercise_upvoted", "Vote utile sur un exercice"
        SOLUTION_ATTEMPT = "solution_attempt", "Tentative de solution"
        SOLUTION_VALIDATED = "solution_validated", "Solution validée"
        FIRST_VALIDATED = "first_validated", "Première solution validée d'un exercice"
        SOLUTION_UPVOTED = "solution_upvoted", "Vote utile sur une solution"
        SOLUTION_RECOMMENDED = "solution_recommended", "Solution recommandée par l'auteur"
        REVIEW_AGREED = "review_agreed", "Relecture concordante"
        REPORT_CONFIRMED = "report_confirmed", "Signalement confirmé"
        PLAGIARISM_PENALTY = "plagiarism_penalty", "Pénalité de plagiat"
        REVERSAL = "reversal", "Annulation"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_transactions",
    )
    amount = models.IntegerField()
    reason = models.CharField(max_length=32, choices=Reason.choices)
    # Objet à l'origine des points, au format « app.modèle » + identifiant.
    source_type = models.CharField(max_length=64)
    source_id = models.PositiveBigIntegerField()
    level = models.ForeignKey(
        "catalog.Level",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Niveau de l'exercice concerné, pour les classements par niveau.",
    )
    reverses = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reversed_by",
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "reason", "source_type", "source_id"],
                name="point_transaction_idempotent",
            ),
        ]
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self):
        return f"{self.amount:+d} {self.get_reason_display()} → {self.user}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Le ledger est en ajout seul : annuler plutôt que modifier.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Le ledger est en ajout seul : annuler plutôt que supprimer.")


class UserBadge(models.Model):
    """Badge obtenu. Le catalogue et les critères sont dans badges.py."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges"
    )
    badge = models.CharField(max_length=32)
    awarded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["awarded_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "badge"], name="user_badge_unique"),
        ]

    def __str__(self):
        return f"{self.badge} → {self.user}"
