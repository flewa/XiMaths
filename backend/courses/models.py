from django.conf import settings
from django.db import models


class CourseNote(models.Model):
    """Texte de cours écrit par la rédaction (courses/notes/) : une fiche de rappels, ou la
    démonstration d'un théorème. Seule l'équipe le voit tant qu'il n'est pas publié : un
    admin le relit, puis le publie."""

    class Cycle(models.TextChoices):
        SUP = "sup", "Première année (sup)"
        SPE = "spe", "Deuxième année (spé)"

    class Kind(models.TextChoices):
        FICHE = "fiche", "Fiche de rappels"
        DEMONSTRATION = "demonstration", "Démonstration"

    class Status(models.TextChoices):
        """Place d'une démonstration par rapport au programme de prépa (MPSI, MP)."""

        AU_PROGRAMME = "au-programme", "Au programme"
        PREUVE_HORS_PROGRAMME = "preuve-hors-programme", "Énoncé au programme, démonstration hors programme"
        HORS_PROGRAMME = "hors-programme", "Hors programme"

    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.FICHE)
    status = models.CharField(
        max_length=30, choices=Status.choices, blank=True, help_text="Démonstrations seulement : place au programme."
    )
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    cycle = models.CharField(max_length=3, choices=Cycle.choices)
    programs = models.CharField(
        max_length=100, help_text="Filières dont le programme couvre la fiche, par exemple « MP, PSI »."
    )
    position = models.PositiveSmallIntegerField(default=0, help_text="Rang dans le sommaire du cycle.")
    topic = models.ForeignKey(
        "catalog.Topic",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="course_notes",
        help_text="Chapitre ou notion du site : la fiche publiée y est proposée.",
    )
    body = models.TextField(help_text="Markdown et LaTeX, comme les énoncés.")
    # Empreinte du fichier importé : l'import ne réécrit la fiche que si le fichier a changé.
    source_hash = models.CharField(max_length=64, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["cycle", "position", "title"]
        verbose_name = "fiche de rappels de cours"
        verbose_name_plural = "fiches de rappels de cours"

    def __str__(self):
        return self.title

    @property
    def published(self):
        return self.published_at is not None
