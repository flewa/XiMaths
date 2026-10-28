"""Job nocturne de la progression.

- Promeut au niveau Membre les nouveaux comptes qui ont désormais 7 jours et 30 points :
  l'ancienneté s'acquiert sans événement qui déclencherait la promotion.
- Attribue les badges manquants, en filet de sécurité des vérifications faites
  après chaque événement (et pour les données créées avant les badges).
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from gamification.badges import check_badges
from gamification.services import promote_new_member

User = get_user_model()


class Command(BaseCommand):
    help = "Promeut les nouveaux membres et attribue les badges manquants."

    def handle(self, *args, **options):
        promoted = sum(
            promote_new_member(user)
            for user in User.objects.filter(trust_level=User.TrustLevel.NEW, is_active=True).iterator()
        )
        badges = sum(len(check_badges(user)) for user in User.objects.filter(is_active=True).iterator())
        self.stdout.write(
            self.style.SUCCESS(f"{promoted} nouveau(x) membre(s), {badges} badge(s) attribué(s).")
        )
