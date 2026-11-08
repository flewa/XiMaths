"""Importe les fiches de rappels de cours de la rédaction (courses/notes/). Les nouvelles
arrivent en brouillon, visibles de l'équipe seulement ; une fiche dont le texte a changé
repasse en brouillon, pour être relue avant d'être publiée de nouveau.

    python manage.py import_course_notes --dry-run   # vérifie les fichiers, n'écrit rien
    python manage.py import_course_notes
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.services import import_sources
from courses.sources import load_sources


class Command(BaseCommand):
    help = "Importe les fiches de rappels de cours de la rédaction."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Vérifie les fichiers sans rien écrire.")

    def handle(self, *args, dry_run=False, **options):
        try:
            sources = load_sources()
            if dry_run:
                self.stdout.write(f"{len(sources)} fiches valides. Rien n'a été écrit.")
                return
            with transaction.atomic():
                created, updated, unpublished = import_sources(sources)
        except ValueError as error:
            raise CommandError(str(error)) from error
        line = f"Rappels de cours : {created} nouvelles, {updated} mises à jour."
        if unpublished:
            line += f" Repassées en brouillon (texte modifié) : {unpublished}."
        self.stdout.write(line)
