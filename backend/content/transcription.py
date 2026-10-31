"""Photo d'une copie manuscrite transcrite en Markdown et LaTeX, que l'auteur relit
avant de publier.

Claude Opus lit la photo ; il transcrit sans corriger ni compléter. La photo n'est pas
conservée : elle part à Claude, puis seule la transcription revient à l'auteur.
"""

import base64

from config import llm
from config.errors import RuleError

from .models import TEXT_MAX_LENGTH

MAX_BYTES = 5 * 1024 * 1024
# Signatures des formats lus par Claude : (début du fichier, type MIME).
SIGNATURES = (
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
)
TIMEOUT = 45


class TranscriptionUnavailable(Exception):
    """Pas de LLM configuré, ou pas de réponse exploitable : rien à reprocher à la photo."""

SYSTEM = (
    "Tu transcris la photo d'une copie manuscrite de mathématiques en Markdown, avec LaTeX "
    "entre $…$ en ligne et $$…$$ en bloc, pour que l'étudiant qui l'a écrite la relise puis "
    "la publie comme sa solution. Transcris fidèlement ce qui est écrit, dans l'ordre : ne "
    "corrige rien, ne complète rien, n'ajoute ni étape, ni explication, ni commentaire, même "
    "si le raisonnement est faux ou inachevé. Garde la langue, les notations et l'organisation "
    "(paragraphes, étapes numérotées, encadrés en gras). Ignore ce qui est barré. Remplace un "
    "passage que tu ne peux pas lire par [illisible]. L'énoncé de l'exercice est fourni pour "
    "reconnaître les notations : ne le recopie pas. Si la photo ne montre pas de mathématiques "
    "manuscrites lisibles, réponds avec legible à false et un texte vide."
)
SCHEMA = {
    "type": "object",
    "properties": {"legible": {"type": "boolean"}, "text": {"type": "string"}},
    "required": ["legible", "text"],
    "additionalProperties": False,
}


def media_type(data):
    """Type MIME d'après les premiers octets, ou None pour un format non lu."""
    for signature, mime in SIGNATURES:
        if data.startswith(signature):
            return mime
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def transcribe(exercise, data):
    """Transcription de la photo `data` (octets), pour une solution de `exercise`."""
    if not llm.enabled():
        raise TranscriptionUnavailable("La transcription des photos n'est pas disponible pour le moment.")
    if len(data) > MAX_BYTES:
        raise RuleError("Photo trop lourde : 5 Mo au plus.")
    mime = media_type(data)
    if mime is None:
        raise RuleError("Format non reconnu : envoie une photo JPEG, PNG ou WebP.")
    answer = llm.ask_json(
        llm.TRANSCRIPTION_MODEL,
        system=SYSTEM,
        prompt=[
            {
                "type": "image",
                "source": {"type": "base64", "media_type": mime, "data": base64.b64encode(data).decode()},
            },
            {"type": "text", "text": f"Énoncé de l'exercice « {exercise.title} » :\n\n{exercise.statement}"},
        ],
        schema=SCHEMA,
        effort="medium",
        timeout=TIMEOUT,
    )
    if answer is None:
        raise TranscriptionUnavailable("La transcription a échoué. Réessaie dans un instant, ou tape ta solution.")
    text = answer.get("text", "").strip()
    if not answer.get("legible") or not text:
        raise RuleError("Rien de lisible sur cette photo : reprends-la de plus près, bien éclairée et nette.")
    return text[:TEXT_MAX_LENGTH]
