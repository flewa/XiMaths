from django.conf import settings
from django.db import models
from django.db.models import Q

from content.models import Exercise, Solution
from duplicates.models import DuplicatePair


class Report(models.Model):
    """Signalement d'un exercice ou d'une solution par un membre.

    Un doublon se tranche dans la file des doublons, où le signalement ouvre une
    paire ; les autres motifs se tranchent ici. Toute décision est humaine et motivée.
    """

    class Reason(models.TextChoices):
        DUPLICATE = "doublon", "Doublon d'un autre exercice"
        PLAGIARISM = "plagiat", "Plagiat"
        ERROR = "erreur", "Erreur mathématique"
        INAPPROPRIATE = "inapproprie", "Contenu inapproprié"
        UNDECLARED_AI = "ia_non_declaree", "Usage de l'IA non déclaré"

    class Status(models.TextChoices):
        OPEN = "ouvert", "À traiter"
        CONFIRMED = "confirme", "Confirmé"
        REJECTED = "rejete", "Non retenu"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_made", verbose_name="signalé par"
    )
    exercise = models.ForeignKey(
        Exercise, null=True, blank=True, on_delete=models.CASCADE, related_name="reports", verbose_name="exercice"
    )
    solution = models.ForeignKey(
        Solution, null=True, blank=True, on_delete=models.CASCADE, related_name="reports", verbose_name="solution"
    )
    reason = models.CharField("motif", max_length=16, choices=Reason.choices)
    details = models.TextField("précisions", max_length=1000, blank=True)
    duplicate_pair = models.ForeignKey(
        DuplicatePair,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports",
        verbose_name="paire de doublons",
    )
    status = models.CharField("statut", max_length=16, choices=Status.choices, default=Status.OPEN)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="tranché par",
    )
    decided_at = models.DateTimeField("tranché le", null=True, blank=True)
    decision_note = models.TextField(
        "motif de la décision", blank=True, help_text="Communiqué à l'auteur du contenu en cas de retrait."
    )
    created_at = models.DateTimeField("signalé le", auto_now_add=True)

    class Meta:
        verbose_name = "signalement"
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(exercise__isnull=False, solution__isnull=True)
                | Q(exercise__isnull=True, solution__isnull=False),
                name="report_single_target",
            ),
            models.UniqueConstraint(
                fields=["reporter", "exercise", "reason"],
                condition=Q(status="ouvert", exercise__isnull=False),
                name="report_open_unique_exercise",
            ),
            models.UniqueConstraint(
                fields=["reporter", "solution", "reason"],
                condition=Q(status="ouvert", solution__isnull=False),
                name="report_open_unique_solution",
            ),
        ]

    def __str__(self):
        return f"{self.get_reason_display()} : {self.target}"

    @property
    def target(self):
        return self.exercise or self.solution
