from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Événement qui concerne directement un membre. Jamais de relance marketing."""

    class Kind(models.TextChoices):
        REVIEW_ASSIGNED = "relecture_attribuee", "Relecture attribuée"
        REVIEW_REMINDER = "relecture_relance", "Relecture en attente"
        SOLUTION_VALIDATED = "solution_validee", "Solution validée"
        SOLUTION_NEEDS_WORK = "solution_a_completer", "Solution à compléter"
        SOLUTION_HELD = "solution_en_verification", "Solution en vérification"
        EXERCISE_SOLVED = "exercice_resolu", "Ton exercice est résolu"
        SOLUTION_RECOMMENDED = "solution_recommandee", "Solution recommandée"
        BADGE = "badge", "Badge"
        PROMOTION = "promotion", "Nouveau niveau de confiance"
        CONTENT_REMOVED = "contenu_retire", "Contenu retiré"
        REPORT_RESOLVED = "signalement_traite", "Signalement traité"
        DUPLICATE_MERGED = "doublon_fusionne", "Exercice fusionné"
        SANCTION = "sanction", "Décision de modération"
        APPEAL_DECIDED = "appel_tranche", "Appel tranché"
        COMPREHENSION_QUESTION = "question_comprehension", "Question de compréhension"
        CHALLENGE = "defi", "Défi du jour"
        GOAL = "objectif", "Objectif"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=32, choices=Kind.choices)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=300, blank=True, help_text="Chemin dans le front, par exemple /relectures.")
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    # Email à envoyer : immédiatement, ou à 8 h si l'événement tombe en heures calmes.
    email_pending = models.BooleanField(default=False)
    emailed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [models.Index(fields=["user", "read_at"]), models.Index(fields=["email_pending"])]

    def __str__(self):
        return f"{self.get_kind_display()} → {self.user}"


class DigestLog(models.Model):
    """Résumé hebdomadaire déjà envoyé : un par membre et par semaine."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    week = models.CharField(max_length=8, help_text="Semaine ISO, « 2026-W44 ».")
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "week"], name="digest_once_per_week")]
