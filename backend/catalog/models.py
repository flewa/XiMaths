from django.db import models


class Level(models.Model):
    """Niveau d'études : licence, master ou filière de prépa."""

    class Track(models.TextChoices):
        UNIVERSITY = "universite", "Université"
        PREPA = "prepa", "Classe préparatoire"

    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=64)
    track = models.CharField(max_length=16, choices=Track.choices)
    year = models.PositiveSmallIntegerField(
        help_text="Année d'études après le bac : rend les niveaux comparables (MP ≈ L2 = 2)."
    )
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.code


class Topic(models.Model):
    """Chapitre, rangé dans une arborescence (Analyse › Séries › Séries entières)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
