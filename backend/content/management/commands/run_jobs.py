"""Tâches planifiées de XiMaths.

- `run_jobs hourly` : défis du jour à ouvrir et tentatives à rendre, relectures en
  retard, fin des sanctions, emails retenus pendant les heures calmes, résumé
  hebdomadaire du lundi matin.
- `run_jobs nightly` : bilan de la semaine écoulée (séries), doublons, progression
  et badges, purges.
- `run_jobs --loop` : pour le conteneur planificateur ; les tâches horaires chaque
  heure, et les nocturnes à 3 h, heure de Paris.

Une tâche qui échoue est journalisée sans empêcher les suivantes.
"""

import logging
import time
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from content.services import review_deadlines
from gamification.rankings import Week
from gamification.streaks import close_week
from moderation.services import comprehension_tick, lift_expired, purge_signals
from notifications.services import in_quiet_hours, purge_old, send_digests, send_pending_emails
from training.challenges import open_challenges
from training.services import close_expired

logger = logging.getLogger("ximaths.jobs")

NIGHTLY_HOUR = 3


def weekly_digests(now):
    # Le lundi, une fois les heures calmes passées ; DigestLog évite tout doublon.
    if timezone.localtime(now).weekday() != 0 or in_quiet_hours(now):
        return 0
    return send_digests(now=now)


HOURLY = {
    "défis du jour à ouvrir": lambda now: len(open_challenges(now=now)),
    "défis à rendre (échéance passée)": lambda now: close_expired(now=now),
    "relectures en retard (relances, réattributions)": lambda now: review_deadlines(now=now),
    "sanctions arrivées à échéance": lambda now: lift_expired(now=now),
    "questions de compréhension (rédaction, délais, préévaluation)": lambda now: comprehension_tick(now=now),
    "emails retenus pendant les heures calmes": lambda now: send_pending_emails(now=now),
    "résumés hebdomadaires": weekly_digests,
}

NIGHTLY = {
    # Idempotent : la semaine écoulée est close dès le lundi, une seule fois.
    "séries de la semaine écoulée": lambda now: close_week(Week.containing(now).shifted(-1), now=now),
    "doublons": lambda now: call_command("scan_duplicates"),
    "progression et badges": lambda now: call_command("refresh_progress"),
    "notifications de plus de 6 mois": lambda now: purge_old(now=now),
    "signaux d'intégrité tranchés depuis un an": lambda now: purge_signals(now=now),
    "sessions expirées": lambda now: call_command("clearsessions"),
}


def run(jobs, now):
    """Lance chaque tâche ; renvoie le nombre d'échecs."""
    failures = 0
    for name, job in jobs.items():
        try:
            result = job(now)
            logger.info("%s : %s", name, "fait" if result is None else result)
        except Exception:
            logger.exception("Échec de la tâche « %s »", name)
            failures += 1
    return failures


def next_hour(now):
    return (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)


class Command(BaseCommand):
    help = "Lance les tâches planifiées : hourly, nightly, ou --loop pour un planificateur."

    def add_arguments(self, parser):
        parser.add_argument("group", nargs="?", choices=["hourly", "nightly"])
        parser.add_argument("--loop", action="store_true", help="Tourne indéfiniment, à chaque heure pile.")

    def handle(self, *args, group=None, loop=False, **options):
        if loop:
            return self.loop()
        if group is None:
            self.stderr.write("Précise hourly, nightly ou --loop.")
            return
        failures = run(HOURLY if group == "hourly" else NIGHTLY, timezone.now())
        if failures:
            raise SystemExit(1)

    def loop(self):
        logger.info("Planificateur démarré.")
        while True:
            now = timezone.now()
            run(HOURLY, now)
            if timezone.localtime(now).hour == NIGHTLY_HOUR:
                run(NIGHTLY, now)
            time.sleep(max(1, (next_hour(timezone.now()) - timezone.now()).total_seconds()))
