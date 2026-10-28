"""Embedding E1 des énoncés : bge-m3, servi par Text Embeddings Inference (TEI).

Sans EMBEDDINGS_URL, ou si le service ne répond pas, la détection se rabat sur
les seules signatures MinHash : les bandes « très similaire » et « peut-être lié »
ne sont alors pas détectées.
"""

import json
import logging
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings

DIMENSIONS = 1024

logger = logging.getLogger(__name__)


def embed(text):
    """Vecteur normalisé de l'énoncé, ou None si le service est absent."""
    if not settings.EMBEDDINGS_URL:
        return None
    request = Request(
        f"{settings.EMBEDDINGS_URL.rstrip('/')}/embed",
        data=json.dumps({"inputs": text, "normalize": True, "truncate": True}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=settings.EMBEDDINGS_TIMEOUT) as response:
            vector = json.load(response)[0]
    except (URLError, TimeoutError, ValueError, IndexError, KeyError) as error:
        logger.warning("Service d'embeddings indisponible : %s", error)
        return None
    if len(vector) != DIMENSIONS:
        logger.error("Embedding de dimension %s, %s attendue.", len(vector), DIMENSIONS)
        return None
    return vector
