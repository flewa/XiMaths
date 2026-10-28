"""Job nocturne de la détection de doublons.

1. Indexe les exercices publiés sans empreintes, ou dont les empreintes sont
   périmées : normalisation modifiée, ou embedding absent alors que le service est configuré.
2. Avec un LLM configuré : résumés canoniques manquants (E2), puis avis du LLM sur les
   paires à arbitrer des bandes « quasi-copie » et « très similaire ».
3. Compare les exercices publiés récemment au stock et ouvre les paires à arbitrer.
   Une paire déjà ouverte ou tranchée n'est jamais reproposée.
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from content.models import Exercise
from duplicates.llm import arbitrate_pending, index_summaries
from duplicates.services import NORMALIZATION_VERSION, index_exercise, scan


class Command(BaseCommand):
    help = "Indexe les exercices publiés et ouvre les paires de doublons à arbitrer."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=2, help="Compare les exercices publiés depuis N jours (2 par défaut)."
        )
        parser.add_argument("--all", action="store_true", help="Compare tous les exercices publiés.")
        parser.add_argument(
            "--reindex",
            action="store_true",
            help="Recalcule toutes les empreintes, après un changement de normalisation ou de modèle.",
        )

    def handle(self, *args, **options):
        published = Exercise.objects.filter(status=Exercise.Status.PUBLISHED)
        stale = Q(fingerprint__isnull=True) | ~Q(fingerprint__version=NORMALIZATION_VERSION)
        if settings.EMBEDDINGS_URL:
            stale |= Q(fingerprint__embedding__isnull=True)
        indexed = 0
        for exercise in (published if options["reindex"] else published.filter(stale)).iterator():
            index_exercise(exercise)
            indexed += 1

        recent = published
        if not options["all"]:
            recent = published.filter(published_at__gte=timezone.now() - timedelta(days=options["days"]))
        # Avec un LLM : résumés canoniques (E2) d'abord, pour qu'ils servent au scan.
        summarized = index_summaries()
        opened = scan(recent.select_related("fingerprint"))
        arbitrated = arbitrate_pending()
        self.stdout.write(
            self.style.SUCCESS(
                f"{indexed} exercice(s) indexé(s), {summarized} résumé(s) canonique(s), "
                f"{opened} paire(s) à arbitrer ouverte(s), {arbitrated} avis du LLM."
            )
        )
