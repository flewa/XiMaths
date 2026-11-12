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


class IntegritySignal(models.Model):
    """Signal d'intégrité tranché par un modérateur : un historique. La détection automatique
    comparait des textes ; les copies sont désormais des photos, et un plagiat se signale
    par un relecteur (Report). Les décisions passées restent visibles de leur auteur, qui
    peut faire appel ; elles s'effacent un an après."""

    class Kind(models.TextChoices):
        PLAGIARISM = "plagiat", "Ressemblance avec une solution antérieure"
        EXTERNAL_PASTE = "collage_externe", "Collage externe"
        ABNORMAL_TIME = "temps_anormal", "Temps anormal"
        AI_FINGERPRINT = "empreinte_ia", "Proche d'une sortie d'IA"

    class Status(models.TextChoices):
        OPEN = "ouvert", "À examiner"
        CLEARED = "leve", "Levé"
        CONFIRMED = "confirme", "Confirmé"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="integrity_signals", verbose_name="membre"
    )
    solution = models.ForeignKey(
        Solution, null=True, blank=True, on_delete=models.CASCADE, related_name="integrity_signals"
    )
    kind = models.CharField("type", max_length=16, choices=Kind.choices)
    value = models.FloatField("valeur", help_text="Pour un plagiat : l'indice de Jaccard.")
    matched_solution = models.ForeignKey(
        Solution,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="solution ressemblante",
    )
    author_answer = models.TextField("réponse de l'auteur", blank=True, max_length=2000)
    status = models.CharField("statut", max_length=16, choices=Status.choices, default=Status.OPEN)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField("motif de la décision", blank=True)
    created_at = models.DateTimeField("signalé le", auto_now_add=True)

    class Meta:
        verbose_name = "signal d'intégrité"
        verbose_name_plural = "signaux d'intégrité"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} · {self.user}"


class Sanction(models.Model):
    """Décision de modération envers un membre, toujours humaine et motivée.
    Échelle : avertissement, exclusion des classements 30 jours, suspension 7 jours,
    bannissement."""

    class Kind(models.TextChoices):
        WARNING = "avertissement", "Avertissement"
        LEADERBOARD_BAN = "exclusion_classements", "Exclusion des classements (30 jours)"
        SUSPENSION = "suspension", "Suspension (7 jours)"
        BAN = "bannissement", "Bannissement"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sanctions", verbose_name="membre"
    )
    kind = models.CharField("sanction", max_length=24, choices=Kind.choices)
    reason = models.TextField("motif", help_text="Communiqué au membre : type de signal, contenus concernés.")
    report = models.ForeignKey(Report, null=True, blank=True, on_delete=models.SET_NULL, related_name="sanctions")
    starts_at = models.DateTimeField("début")
    ends_at = models.DateTimeField("fin", null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+", verbose_name="décidée par"
    )
    lifted_at = models.DateTimeField("levée le", null=True, blank=True)
    lifted_reason = models.CharField("raison de la levée", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} · {self.user}"


class Appeal(models.Model):
    """Appel d'une décision (sanction, retrait d'un contenu, plagiat confirmé), sous
    14 jours. Un autre modérateur l'examine et répond sous 7 jours."""

    class Status(models.TextChoices):
        PENDING = "en_attente", "En attente"
        UPHELD = "maintenue", "Décision maintenue"
        OVERTURNED = "annulee", "Décision annulée"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appeals")
    sanction = models.OneToOneField(Sanction, null=True, blank=True, on_delete=models.CASCADE, related_name="appeal")
    report = models.OneToOneField(Report, null=True, blank=True, on_delete=models.CASCADE, related_name="appeal")
    signal = models.OneToOneField(
        IntegritySignal, null=True, blank=True, on_delete=models.CASCADE, related_name="appeal"
    )
    message = models.OneToOneField(
        "content.Message", null=True, blank=True, on_delete=models.CASCADE, related_name="appeal"
    )
    statement = models.TextField("arguments du membre", max_length=3000)
    status = models.CharField("statut", max_length=16, choices=Status.choices, default=Status.PENDING)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    decision_note = models.TextField("motif de la décision", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "appel"
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(sanction__isnull=False, report__isnull=True, signal__isnull=True, message__isnull=True)
                    | Q(sanction__isnull=True, report__isnull=False, signal__isnull=True, message__isnull=True)
                    | Q(sanction__isnull=True, report__isnull=True, signal__isnull=False, message__isnull=True)
                    | Q(sanction__isnull=True, report__isnull=True, signal__isnull=True, message__isnull=False)
                ),
                name="appeal_single_decision",
            ),
        ]

    def __str__(self):
        return f"Appel de {self.user} ({self.get_status_display()})"

    @property
    def decision(self):
        return self.sanction or self.report or self.signal or self.message


class ModerationLog(models.Model):
    """Journal des décisions de l'équipe, lisible par toute l'équipe : qui a décidé quoi,
    et pourquoi. Écrit par les services, jamais modifié."""

    class Action(models.TextChoices):
        REPORT_CONFIRMED = "signalement_confirme", "Signalement confirmé"
        REPORT_REJECTED = "signalement_rejete", "Signalement non retenu"
        MESSAGE_REMOVED = "message_retire", "Message retiré"
        FLAGS_DISMISSED = "message_garde", "Message gardé"
        SANCTION = "sanction", "Sanction"
        SANCTION_LIFTED = "sanction_levee", "Sanction levée"
        APPEAL_UPHELD = "appel_rejete", "Appel rejeté"
        APPEAL_OVERTURNED = "appel_accepte", "Appel accepté"
        MODERATOR_NAMED = "moderateur_nomme", "Modérateur nommé"
        MODERATOR_REMOVED = "moderateur_retire", "Modérateur retiré"
        SOLUTION_DECIDED = "copie_decidee", "Copie décidée par l'administration"
        EXERCISE_EDITED = "exercice_modifie", "Exercice modifié"
        EXERCISE_RESTORED = "exercice_retabli", "Exercice rétabli"
        POINTS_ADJUSTED = "points_ajustes", "Points ajustés"
        TRUST_CHANGED = "niveau_change", "Niveau de confiance changé"
        EMAIL_VERIFIED = "email_verifie", "Adresse vérifiée à la main"
        ACCOUNT_RENAMED = "compte_renomme", "Pseudo changé"
        ACCOUNT_DELETED = "compte_supprime", "Compte supprimé"
        ADMIN_NAMED = "admin_nomme", "Administrateur nommé"
        ADMIN_REMOVED = "admin_retire", "Administrateur retiré"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+", verbose_name="par"
    )
    action = models.CharField(max_length=32, choices=Action.choices)
    # Le membre concerné, s'il y en a un : sa fiche de modération reprend ces lignes.
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="moderation_log"
    )
    summary = models.TextField("résumé")
    url = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "entrée du journal de modération"
        verbose_name_plural = "journal de modération"
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return f"{self.get_action_display()} · {self.summary[:60]}"


class ComprehensionQuestion(models.Model):
    """Question de compréhension sur sa propre solution, quand le score d'intégrité
    d'une solution classée ou à fort enjeu dépasse le seuil. On prouve la
    compréhension, pas l'auteur : sans réponse ou insuffisante, la solution reste
    publiée, sans ses points de classement. Jamais de sanction."""

    class Status(models.TextChoices):
        TO_WRITE = "a_rediger", "À rédiger"
        SENT = "envoyee", "Envoyée"
        OPENED = "ouverte", "Ouverte"
        ANSWERED = "repondue", "À évaluer"
        PASSED = "reussie", "Réussie"
        FAILED = "insuffisante", "Insuffisante"
        EXPIRED = "sans_reponse", "Sans réponse"
        DROPPED = "abandonnee", "Abandonnée"

    class Assessment(models.TextChoices):
        CONVINCING = "convaincante", "Convaincante"
        PARTIAL = "partielle", "Partielle"
        INSUFFICIENT = "insuffisante", "Insuffisante"

    solution = models.OneToOneField(Solution, on_delete=models.CASCADE, related_name="comprehension_question")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comprehension_questions", verbose_name="membre"
    )
    integrity_score = models.FloatField("score d'intégrité")
    question = models.TextField("question", blank=True, help_text="Sur un choix précis de la solution, sans accusation.")
    expected_points = models.JSONField(
        "éléments attendus", default=list, blank=True, help_text="Pour l'évaluateur, jamais montrés au membre."
    )
    generated_by_llm = models.BooleanField(default=False)
    status = models.CharField("statut", max_length=16, choices=Status.choices, default=Status.TO_WRITE)
    sent_at = models.DateTimeField("envoyée le", null=True, blank=True)
    opened_at = models.DateTimeField("ouverte le", null=True, blank=True)
    answered_at = models.DateTimeField("répondue le", null=True, blank=True)
    answer = models.TextField("réponse", blank=True, max_length=3000)
    llm_assessment = models.CharField(
        "préévaluation du LLM", max_length=16, choices=Assessment.choices, blank=True
    )
    llm_rationale = models.TextField("motif de la préévaluation", blank=True)
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    evaluated_at = models.DateTimeField(null=True, blank=True)
    evaluation_note = models.TextField("motif de l'évaluation", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "question de compréhension"
        verbose_name_plural = "questions de compréhension"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Question à {self.user} ({self.get_status_display()})"
