"""Classements, calculés à la demande depuis le ledger.

- Semaine du lundi 0 h au dimanche 23 h 59, heure de Paris.
- Les points d'une écriture comptent pour le niveau principal de l'exercice
  concerné : un étudiant de L1 qui résout un exercice de M2 marque en M2.
- Une annulation compte dans la semaine de l'écriture qu'elle annule, si elle
  arrive dans les 24 h de consolidation qui suivent la fin de la semaine. Passé
  ce délai, la semaine est définitive.
- Le Panthéon cumule tous les points, depuis l'inscription.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from moderation.models import Sanction

from .models import PointTransaction

User = get_user_model()

CONSOLIDATION = timedelta(hours=24)
TOP_SIZE = 50
NEIGHBOURS = 5
WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")


@dataclass(frozen=True, order=True)
class Week:
    year: int
    number: int

    @classmethod
    def containing(cls, moment=None):
        iso = timezone.localtime(moment).isocalendar()
        return cls(iso.year, iso.week)

    @classmethod
    def parse(cls, label):
        """« 2026-W44 » ; ValueError si la semaine n'existe pas."""
        match = WEEK_RE.match(label)
        if not match:
            raise ValueError(f"Semaine invalide : {label}")
        year, number = int(match[1]), int(match[2])
        date.fromisocalendar(year, number, 1)  # ValueError pour une semaine 53 inexistante.
        return cls(year, number)

    @property
    def label(self):
        return f"{self.year}-W{self.number:02d}"

    @property
    def monday(self):
        return date.fromisocalendar(self.year, self.number, 1)

    @property
    def sunday(self):
        return self.monday + timedelta(days=6)

    @property
    def start(self):
        return timezone.make_aware(datetime.combine(self.monday, time.min))

    @property
    def end(self):
        # Calculé sur les dates : une semaine qui change d'heure dure 167 ou 169 heures.
        return timezone.make_aware(datetime.combine(self.monday + timedelta(days=7), time.min))

    def shifted(self, weeks):
        iso = (self.monday + timedelta(weeks=weeks)).isocalendar()
        return Week(iso.year, iso.week)

    def is_final(self, now=None):
        return (now or timezone.now()) >= self.end + CONSOLIDATION


@dataclass(frozen=True)
class Entry:
    rank: int
    user_id: int
    username: str
    declared_level: str | None
    points: int


def excluded_ids(now=None):
    """Membres exclus des classements par une sanction en cours."""
    return Sanction.objects.filter(
        kind=Sanction.Kind.LEADERBOARD_BAN, lifted_at=None, ends_at__gt=now or timezone.now()
    ).values("user_id")


def ranked_users():
    """Présents dans les classements : membres actifs, sans exclusion en cours, qui
    n'ont pas masqué leur présence."""
    return User.objects.filter(
        is_active=True,
        status=User.Status.ACTIVE,
        trust_level__gte=User.TrustLevel.MEMBER,
        leaderboard_visible=True,
    ).exclude(pk__in=excluded_ids())


def points_by_user(*, week=None, level=None):
    """{user_id: points} sur la semaine (ou depuis toujours), tous niveaux ou un seul."""
    transactions = PointTransaction.objects.all()
    if week is not None:
        transactions = transactions.annotate(
            counted_at=Coalesce("reverses__created_at", "created_at")
        ).filter(
            counted_at__gte=week.start,
            counted_at__lt=week.end,
            # Une annulation est postérieure à l'écriture annulée : borne utile à l'index.
            created_at__gte=week.start,
            created_at__lt=week.end + CONSOLIDATION,
        )
    if level is not None:
        transactions = transactions.filter(level=level)
    rows = transactions.values("user").annotate(points=Sum("amount"))
    return {row["user"]: row["points"] for row in rows}


def standings(*, week=None, level=None, peers_level=None):
    """Classement complet, du premier au dernier. Ex aequo : même rang (1, 2, 2, 4).
    `peers_level` ne garde que ceux qui ont déclaré ce niveau (« mes pairs »)."""
    points = {pk: total for pk, total in points_by_user(week=week, level=level).items() if total > 0}
    users = ranked_users().filter(pk__in=points)
    if peers_level is not None:
        users = users.filter(declared_level=peers_level)
    rows = sorted(
        users.values_list("pk", "username", "declared_level__code"),
        key=lambda row: (-points[row[0]], row[1].lower()),
    )
    entries = []
    for index, (pk, username, declared) in enumerate(rows):
        rank = entries[-1].rank if entries and entries[-1].points == points[pk] else index + 1
        entries.append(Entry(rank, pk, username, declared, points[pk]))
    return entries


def neighbourhood(entries, user_id, size=NEIGHBOURS):
    """(index de l'utilisateur, ses voisins de chaque côté), ou (None, [])."""
    for index, entry in enumerate(entries):
        if entry.user_id == user_id:
            return index, entries[max(0, index - size) : index + size + 1]
    return None, []


def absence_reason(user, *, week=None, where=""):
    """Pourquoi `user` n'apparaît pas dans un classement. `where` : « en MP »…"""
    if not user.leaderboard_visible:
        return "Tu as masqué ta présence dans les classements."
    if user.status != User.Status.ACTIVE or excluded_ids().filter(user_id=user.pk).exists():
        return "Ton compte n'apparaît pas dans les classements pendant une sanction en cours."
    if user.trust_level < User.TrustLevel.MEMBER:
        return "Les classements s'ouvrent au niveau Membre : 7 jours d'ancienneté et 30 points."
    if week is None:
        return "Tu n'as pas encore de points."
    when = "cette semaine-là." if week < Week.containing() else "cette semaine."
    return " ".join(part for part in ("Pas de points", where, when) if part)
