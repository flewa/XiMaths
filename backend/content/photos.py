"""Photos de copie manuscrite jointes à une solution, envoyées au besoin depuis un téléphone.

- Une solution est toujours une copie manuscrite en photos : rien n'est tapé.
- Sur l'ordinateur, l'auteur ouvre un envoi : le QR code affiché porte son jeton. Le
  jeton suffit pour déposer des photos pendant 30 minutes, sans se connecter sur le
  téléphone ; il n'ouvre rien d'autre. En temps limité (entraînement, défi), l'envoi
  suit la session : ouvert pendant le temps imparti et 60 s de grâce, pas au-delà.
- Trois photos au plus. Chacune est redressée, réduite à 2000 pixels de côté et
  réencodée en JPEG : les métadonnées (lieu de la prise, appareil) disparaissent.
- La solution part en relecture avec ses photos ; le texte devient facultatif. Les
  photos d'un envoi jamais utilisé sont effacées au bout d'un jour.
- Une photo se lit comme le texte de sa solution : l'auteur, ses relecteurs, les
  arbitres d'une solution contestée, les évaluateurs de sa question de compréhension,
  les modérateurs ; tout le monde une fois la solution validée.
"""

import base64
import io
import secrets
from datetime import timedelta

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

from accounts.permissions import is_moderator
from config.errors import RuleError

from .models import PhotoUpload, Solution, SolutionPhoto

MAX_PHOTOS = 3
MAX_BYTES = 10 * 1024 * 1024
MAX_EDGE = 2000
# Au-delà, l'image est refusée avant d'être décodée : pas de bombe de décompression.
MAX_PIXELS = 50_000_000
QUALITY = 85
FORMATS = {"JPEG", "PNG", "WEBP"}
UPLOAD_WINDOW = timedelta(minutes=30)
KEEP_UNUSED = timedelta(days=1)
# Avec des photos, un texte plus court qu'une demi-page est une note : pas une rédaction
# à comparer aux autres (« voir les photos » ne doit pas passer pour du plagiat).
NOTE_LENGTH = 300


def open_upload(user, exercise, *, now=None):
    now = now or timezone.now()
    return PhotoUpload.objects.create(
        token=secrets.token_urlsafe(32), user=user, exercise=exercise, expires_at=now + UPLOAD_WINDOW
    )


def live_uploads(now=None):
    """Envois encore utilisables : dépôt ouvert, ou photos à joindre."""
    now = now or timezone.now()
    return PhotoUpload.objects.filter(created_at__gt=now - KEEP_UNUSED)


def session_of(upload):
    """La session chronométrée de l'envoi, ou None."""
    return getattr(upload, "timed_session", None)


def reopen(upload, *, now=None):
    """30 minutes de plus pour déposer : les photos déjà reçues restent dans l'envoi.
    Le temps d'une session chronométrée, lui, ne se prolonge pas."""
    if session_of(upload) is not None:
        raise RuleError("Le temps d'une session chronométrée ne se prolonge pas.")
    upload.expires_at = (now or timezone.now()) + UPLOAD_WINDOW
    upload.save(update_fields=["expires_at"])
    return upload


def is_open(upload, now=None):
    session = session_of(upload)
    if session is not None:
        from training.services import accepts_photos

        return accepts_photos(session, now)
    return (now or timezone.now()) < upload.expires_at


def closes_at(upload, now=None):
    """Fin du dépôt, pour l'affichage : en session, la fin du temps imparti (grâce non
    comprise), recalculée d'après le chrono du serveur."""
    session = session_of(upload)
    if session is None:
        return upload.expires_at
    from training.services import remaining_s

    now = now or timezone.now()
    return now + timedelta(seconds=max(remaining_s(session, now), 0)) if session.open else now


def closed_message(upload):
    if session_of(upload) is not None:
        return "Le temps est écoulé : les photos ne sont plus acceptées."
    return "Ce QR code a expiré : affiches-en un nouveau sur ton ordinateur."


def upload_state(upload, now=None):
    """L'envoi tel que le voient l'ordinateur (QR code, photos reçues) et le téléphone."""
    session = session_of(upload)
    return {
        "token": upload.token,
        "exercise_id": upload.exercise_id,
        "exercise_title": upload.exercise.title,
        "expires_at": closes_at(upload, now),
        "open": is_open(upload, now),
        "max_photos": MAX_PHOTOS,
        "timed": session is not None,
        "photos": [
            {"id": photo.pk, "url": upload_photo_url(upload, photo), "width": photo.width, "height": photo.height}
            for photo in pending(upload)
        ],
    }


def pending(upload):
    """Photos de l'envoi pas encore jointes à une solution."""
    return upload.photos.filter(solution=None)


def process(data):
    """Octets d'une photo → (JPEG redressé, réduit et sans métadonnées, largeur, hauteur)."""
    if len(data) > MAX_BYTES:
        raise RuleError("Photo trop lourde : 10 Mo au plus.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in FORMATS:
                raise RuleError("Format non reconnu : envoie une photo JPEG, PNG ou WebP.")
            if image.width * image.height > MAX_PIXELS:
                raise RuleError("Photo trop grande : 50 mégapixels au plus.")
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
            image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
            out = io.BytesIO()
            # Aucun paramètre exif ni icc : le fichier écrit ne garde que l'image.
            image.save(out, "JPEG", quality=QUALITY, optimize=True)
            return out.getvalue(), image.width, image.height
    except RuleError:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise RuleError("Image illisible : reprends la photo, ou envoie-la en JPEG ou en PNG.") from None


@transaction.atomic
def add_photo(upload, data, *, now=None):
    """Dépose une photo dans un envoi encore ouvert."""
    upload = PhotoUpload.objects.select_for_update().get(pk=upload.pk)
    if not is_open(upload, now):
        raise RuleError(closed_message(upload))
    count = pending(upload).count()
    if count >= MAX_PHOTOS:
        raise RuleError(f"{MAX_PHOTOS} photos au plus : retire-en une pour en ajouter une autre.")
    jpeg, width, height = process(data)
    photo = SolutionPhoto(upload=upload, width=width, height=height, position=count)
    photo.image.save("copie.jpg", ContentFile(jpeg), save=False)
    photo.save()
    return photo


def remove_photo(upload, photo_id):
    photo = pending(upload).filter(pk=photo_id).first()
    if photo is None:
        raise RuleError("Cette photo n'est plus dans l'envoi.")
    photo.delete()
    # Positions recalculées : l'ordre de la copie reste celui de la prise.
    for position, kept in enumerate(pending(upload)):
        if kept.position != position:
            kept.position = position
            kept.save(update_fields=["position"])


def upload_for(user, exercise, token, *, now=None):
    """L'envoi `token` de l'auteur pour cet exercice, encore utilisable, ou une erreur."""
    # Les photos d'une session chronométrée sont rendues avec elle, pas ailleurs.
    upload = live_uploads(now).filter(token=token, user=user, exercise=exercise, timed_session=None).first()
    if upload is None:
        raise RuleError("Photos introuvables ou trop anciennes : envoie-les de nouveau.")
    return upload


def attach(upload, solution):
    """Joint les photos de l'envoi à la solution, à la place des précédentes."""
    photos = list(pending(upload))
    for old in solution.photos.exclude(pk__in=[photo.pk for photo in photos]):
        old.delete()
    for position, photo in enumerate(photos):
        photo.solution = solution
        photo.position = position
        photo.save(update_fields=["solution", "position"])
    return photos


def is_note(solution):
    """Texte court accompagnant des photos : une note, pas une rédaction."""
    return len(solution.body.strip()) < NOTE_LENGTH and solution.photos.exists()


def can_view(user, solution, *, now=None):
    """Une copie est privée, même validée : son auteur, ses relecteurs et la modération
    (dont les experts qui évaluent une question de compréhension) la voient."""
    if not user.is_authenticated:
        return False
    if solution.author_id == user.pk or is_moderator(user):
        return True
    if solution.reviews.filter(reviewer=user).exists():
        return True
    if user.trust_level >= user.TrustLevel.EXPERT:
        # Évaluation d'une question de compréhension.
        return Solution.objects.filter(pk=solution.pk, comprehension_question__isnull=False).exists()
    return False


def photo_url(photo):
    return f"/api/solutions/{photo.solution_id}/photos/{photo.pk}"


def upload_photo_url(upload, photo):
    return f"/api/photo-uploads/{upload.token}/photos/{photo.pk}"


def described(solution):
    """Photos d'une solution pour l'API : adresse et dimensions, dans l'ordre de la copie."""
    return [
        {"id": photo.pk, "url": photo_url(photo), "width": photo.width, "height": photo.height}
        for photo in solution.photos.all()
    ]


def llm_blocks(solution):
    """Les photos de la solution en blocs image, pour Claude."""
    blocks = []
    for photo in solution.photos.all():
        with photo.image.open("rb") as file:
            data = base64.b64encode(file.read()).decode()
        blocks.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}})
    return blocks


def purge(*, now=None):
    """Efface les photos jamais jointes et les envois de plus d'un jour."""
    now = now or timezone.now()
    old = PhotoUpload.objects.filter(created_at__lte=now - KEEP_UNUSED)
    # Une à une, pour que chaque fichier parte avec sa ligne (signal post_delete).
    photos = SolutionPhoto.objects.filter(Q(upload__in=old) | Q(upload=None), solution=None)
    count = 0
    for photo in photos:
        photo.delete()
        count += 1
    old.delete()
    return count
