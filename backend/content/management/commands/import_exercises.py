"""Publie les exercices de la rédaction (content/editorial/, un fichier par lot) sous le compte « XiMaths ».

Chaque exercice passe par la même validation qu'un exercice proposé sur le site (schéma
de l'API, commandes LaTeX interdites, niveaux et chapitres connus), puis par la détection
de doublons : un exercice trop proche d'un exercice déjà publié est laissé de côté et
signalé. La commande peut être relancée : ce que la rédaction a déjà publié n'est pas recréé,
mais prend son titre actuel (retrouvé par `former_titles` s'il a changé) et ses chapitres et
notions.

    python manage.py import_exercises --dry-run   # vérifie tout, n'écrit rien
    python manage.py import_exercises
"""

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from ninja.errors import HttpError
from pydantic import ValidationError

from content.api import ExerciseIn, draft_fields
from content.editorial import EXERCISES
from content.models import Exercise
from duplicates.services import DuplicateSuspected, publish_checked
from training.answers import check_answer
from training.challenges import check_template, open_challenges
from training.models import ChallengeTemplate

User = get_user_model()

EDITORIAL_USERNAME = "XiMaths"
# Adresse jamais distribuée (domaine réservé .invalid) : le compte ne reçoit aucun email,
# et toutes ses notifications par email sont coupées.
EDITORIAL_EMAIL = "redaction@ximaths.invalid"


def payload(spec):
    return ExerciseIn(
        title=spec["title"],
        statement=spec["statement"],
        hints=spec.get("hints", []),
        final_answer=spec.get("final_answer", ""),
        difficulty=spec["difficulty"],
        primary_level=spec["primary_level"],
        levels=spec["levels"],
        topics=spec["topics"],
    )


def problems(specs):
    """Erreurs de la liste : celles qu'un auteur verrait sur le site, plus les réponses
    finales et les gabarits que SymPy ne lirait pas."""
    found = []
    titles = [spec["title"] for spec in specs]
    for title in {title for title in titles if titles.count(title) > 1}:
        found.append(f"« {title} » apparaît deux fois.")
    for spec in specs:
        for former in spec.get("former_titles", []):
            if former in titles or sum(former in other.get("former_titles", []) for other in specs) > 1:
                found.append(f"« {spec['title']} » : l'ancien titre « {former} » sert déjà ailleurs.")
    for spec in specs:
        title = spec["title"]
        try:
            draft_fields(payload(spec))
        except ValidationError as error:
            found.append(f"« {title} » : {error.errors()[0]['msg']}")
            continue
        except HttpError as error:
            found.append(f"« {title} » : {error}")
            continue
        answer = spec.get("final_answer", "")
        if answer and check_answer(answer, answer) is not True:
            found.append(f"« {title} » : la réponse finale « {answer} » ne se lit pas.")
        if "challenge" in spec:
            found.extend(f"« {title} », gabarit : {error}" for error in check_template(ChallengeTemplate(**spec["challenge"])))
    return found


def editorial_account():
    account, created = User.objects.get_or_create(
        username=EDITORIAL_USERNAME,
        defaults={
            "email": EDITORIAL_EMAIL,
            "email_verified_at": timezone.now(),
            # La rédaction ne concourt pas : ni classements, ni emails.
            "leaderboard_visible": False,
            "email_notifications": False,
            "weekly_digest": False,
            "daily_challenge_notifications": False,
        },
    )
    if created:
        account.set_unusable_password()
        account.save(update_fields=["password"])
    return account


class Command(BaseCommand):
    help = "Publie les exercices de la rédaction sous le compte « XiMaths »."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Vérifie tout sans rien écrire.")

    def handle(self, *args, dry_run=False, **options):
        errors = problems(EXERCISES)
        if errors:
            raise CommandError("\n".join(errors))
        if dry_run:
            self.stdout.write(f"{len(EXERCISES)} exercices valides. Rien n'a été écrit.")
            return

        author = editorial_account()
        published, already, updated, set_aside = 0, 0, 0, []
        for spec in EXERCISES:
            titles = [spec["title"], *spec.get("former_titles", [])]
            existing = Exercise.objects.filter(author=author, title__in=titles).first()
            if existing is not None:
                already += 1
                updated += self.refresh(existing, spec)
                continue
            try:
                with transaction.atomic():
                    fields, levels, topics = draft_fields(payload(spec))
                    exercise = Exercise.objects.create(author=author, **fields)
                    exercise.levels.set(levels)
                    exercise.topics.set(topics)
                    publish_checked(exercise)
                    if "challenge" in spec:
                        ChallengeTemplate.objects.create(exercise=exercise, **spec["challenge"])
            except DuplicateSuspected as suspected:
                close = ", ".join(f"« {match.exercise.title} »" for match in suspected.matches)
                set_aside.append(f"« {spec['title']} », proche de {close}")
                continue
            published += 1

        # Les défis du jour des niveaux qui viennent de recevoir un gabarit.
        open_challenges()
        self.stdout.write(f"Publiés : {published}. Déjà là : {already}. Mis à jour : {updated}.")
        for line in set_aside:
            self.stdout.write(f"Laissé de côté : {line}")
        # Les rappels de cours de la rédaction suivent le même chemin de mise à jour
        # (deploy/update.sh), en brouillon jusqu'à ce qu'un admin les publie.
        call_command("import_course_notes", stdout=self.stdout)

    @staticmethod
    def refresh(exercise, spec):
        """Titre et chapitres (notions comprises) d'un exercice déjà publié, d'après la
        rédaction. Le reste (énoncé, indications, niveaux) ne bouge pas. 1 s'il a changé."""
        fields, _, topics = draft_fields(payload(spec))
        changed = False
        if exercise.title != fields["title"]:
            exercise.title = fields["title"]
            exercise.save(update_fields=["title"])
            changed = True
        if set(exercise.topics.all()) != set(topics):
            exercise.topics.set(topics)
            changed = True
        return int(changed)
