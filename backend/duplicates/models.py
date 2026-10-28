from django.conf import settings
from django.db import models
from django.db.models import F, Q
from pgvector.django import VectorField

from content.models import Exercise

from .embeddings import DIMENSIONS


class Fingerprint(models.Model):
    """Empreintes d'un énoncé publié : signatures MinHash, embedding E1 de l'énoncé,
    et embedding E2 de son résumé canonique quand un LLM est configuré."""

    exercise = models.OneToOneField(
        Exercise, on_delete=models.CASCADE, primary_key=True, related_name="fingerprint"
    )
    version = models.PositiveSmallIntegerField(
        help_text="Version de la normalisation : tout est réindexé quand elle change."
    )
    canonical = models.TextField(help_text="Énoncé normalisé, entrée de l'embedding.")
    signature = models.JSONField(help_text="MinHash de la version alpha (F).")
    abstract_signature = models.JSONField(help_text="MinHash de la version abstraite (F′).")
    # Index HNSW créé par la migration, sur PostgreSQL seulement.
    embedding = VectorField(dimensions=DIMENSIONS, null=True, blank=True)
    summary = models.TextField(
        "résumé canonique",
        blank=True,
        help_text="Deux ou trois phrases sans notation : objets, hypothèses, conclusion demandée.",
    )
    summary_embedding = VectorField(dimensions=DIMENSIONS, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Empreintes de « {self.exercise} »"


class LshKey(models.Model):
    """Clé d'une bande LSH : deux exercices qui partagent une clé sont candidats."""

    class Kind(models.TextChoices):
        ALPHA = "alpha", "Version alpha (F)"
        ABSTRACT = "abstract", "Version abstraite (F′)"

    fingerprint = models.ForeignKey(Fingerprint, on_delete=models.CASCADE, related_name="lsh_keys")
    kind = models.CharField(max_length=8, choices=Kind.choices)
    key = models.BigIntegerField()

    class Meta:
        indexes = [models.Index(fields=["kind", "key"])]


class DuplicatePair(models.Model):
    """Deux exercices proches. Aucune fusion n'est automatique : les paires
    « c'est différent » et celles du scan attendent l'arbitrage d'un modérateur."""

    class Band(models.TextChoices):
        QUASI_COPY = "quasi_copie", "Quasi-copie"
        VERY_SIMILAR = "tres_similaire", "Très similaire"
        VARIANT = "variante", "Variante paramétrique"
        MAYBE_RELATED = "peut_etre_lie", "Peut-être lié"
        REPORTED = "signalement", "Signalé par un membre"

    class AuthorChoice(models.TextChoices):
        NONE = "", "Aucun (trouvée par le scan)"
        VARIANT = "variante", "C'est une variante"
        DIFFERENT = "different", "C'est différent"

    class Relation(models.TextChoices):
        """Avis du LLM sur la paire, du point de vue du nouvel exercice."""

        IDENTICAL = "identique", "Identique"
        PARAMETRIC = "variante_parametrique", "Variante paramétrique"
        SPECIAL_CASE = "cas_particulier", "Cas particulier de l'existant"
        GENERALIZATION = "generalisation", "Généralisation de l'existant"
        SAME_TOPIC = "meme_theme_distinct", "Même thème, mais distinct"
        DIFFERENT = "different", "Différent"

    class Status(models.TextChoices):
        PENDING = "en_attente", "À arbitrer"
        MERGED = "fusionnes", "Fusionnés"
        VARIANTS = "variantes", "Liés comme variantes"
        DISTINCT = "distincts", "Distincts"

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="duplicate_pairs",
        verbose_name="nouvel exercice",
        help_text="Le plus récent : c'est lui qui disparaît en cas de fusion.",
    )
    existing = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="duplicate_pairs_as_existing",
        verbose_name="exercice existant",
        help_text="Le plus ancien, canonique par défaut.",
    )
    band = models.CharField("bande", max_length=16, choices=Band.choices)
    score = models.FloatField("score s", null=True, blank=True, help_text="Absent sans embedding.")
    jaccard = models.FloatField("J(F)")
    abstract_jaccard = models.FloatField("J(F′)")
    cosine = models.FloatField("cos(E1)", null=True, blank=True)
    author_choice = models.CharField(
        "choix de l'auteur",
        max_length=16,
        choices=AuthorChoice.choices,
        blank=True,
        default=AuthorChoice.NONE,
    )
    author_note = models.CharField("ce qui change, selon l'auteur", max_length=300, blank=True)
    status = models.CharField("statut", max_length=16, choices=Status.choices, default=Status.PENDING)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="tranché par",
    )
    decided_at = models.DateTimeField("tranché le", null=True, blank=True)
    moved_solutions = models.JSONField(
        "solutions déplacées",
        default=list,
        blank=True,
        help_text="Déplacées par la fusion, pour pouvoir l'annuler.",
    )
    created_at = models.DateTimeField("ouverte le", auto_now_add=True)
    # Arbitrage préparé par le LLM, mis en cache : un avis, jamais une décision.
    llm_relation = models.CharField("avis du LLM", max_length=24, choices=Relation.choices, blank=True)
    llm_confidence = models.FloatField("confiance du LLM", null=True, blank=True)
    llm_rationale = models.CharField("justification du LLM", max_length=400, blank=True)
    llm_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "paire de doublons"
        verbose_name_plural = "doublons à arbitrer"
        ordering = [F("score").desc(nulls_last=True), "-jaccard", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["exercise", "existing"], name="duplicate_pair_unique"),
            models.CheckConstraint(
                condition=~Q(exercise=F("existing")), name="duplicate_pair_distinct_exercises"
            ),
        ]

    def __str__(self):
        return f"« {self.exercise} » / « {self.existing} »"
