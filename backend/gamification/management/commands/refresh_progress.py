"""Job nocturne de la progression.

- Promeut les comptes qui remplissent les conditions d'un niveau (Membre, Relecteur,
  Expert) : l'ancienneté s'acquiert sans événement qui déclencherait la promotion.
- Attribue les badges manquants, en filet de sécurité des vérifications faites
  après chaque événement (et pour les données créées avant les badges).
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from gamification.badges import check_badges
from gamification.trust import promote

User = get_user_model()


class Command(BaseCommand):
    help = "Promeut les membres qui remplissent les conditions et attribue les badges manquants."

    def handle(self, *args, **options):
        promoted = sum(
            promote(user) is not None
            for user in User.objects.filter(is_active=True, trust_level__lt=User.TrustLevel.MODERATOR).iterator()
        )
        badges = sum(len(check_badges(user)) for user in User.objects.filter(is_active=True).iterator())
        self.stdout.write(
            self.style.SUCCESS(f"{promoted} promotion(s), {badges} badge(s) attribué(s).")
        )
