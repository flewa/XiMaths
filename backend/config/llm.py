"""Client Claude, facultatif. Sans ANTHROPIC_API_KEY, rien n'est appelé et chaque
appelant garde son chemin sans LLM : décision humaine seule, question rédigée par un
modérateur, score de similarité sans résumé canonique.

Les réponses sont du JSON contraint par un schéma (structured outputs). Un refus,
une erreur réseau ou une réponse inexploitable renvoient None : le LLM prépare,
il ne décide jamais seul.
"""

import json
import logging
from functools import cache

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

# Modèles du document de conception : Sonnet arbitre les doublons, Haiku écrit les
# résumés canoniques. Les questions de compréhension, qui portent sur le raisonnement
# d'une solution, reviennent à Opus.
ARBITRATION_MODEL = "claude-sonnet-5-5"
SUMMARY_MODEL = "claude-haiku-5-5"
COMPREHENSION_MODEL = "claude-opus-5-5"
# Haiku n'a pas de repli côté serveur : un refus y reste un refus.
WITHOUT_FALLBACK = {SUMMARY_MODEL}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def enabled():
    return bool(settings.ANTHROPIC_API_KEY)


@cache
def _client(api_key, timeout):
    return anthropic.Anthropic(api_key=api_key, timeout=timeout, max_retries=2)


def ask_json(model, *, system, prompt, schema, effort, max_tokens=16000):
    """Réponse JSON conforme à `schema`, ou None (LLM absent, refus, erreur)."""
    if not enabled():
        return None
    client = _client(settings.ANTHROPIC_API_KEY, settings.LLM_TIMEOUT)
    params = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}},
    }
    try:
        if model in WITHOUT_FALLBACK:
            response = client.messages.create(**params)
        else:
            # Une demande déclinée par les classifieurs est rejouée sur le modèle de repli recommandé.
            response = client.beta.messages.create(betas=[FALLBACK_BETA], fallbacks="default", **params)
    except anthropic.RateLimitError:
        logger.warning("Claude %s : limite de débit atteinte, nouvel essai au prochain passage.", model)
        return None
    except anthropic.APIStatusError as error:
        logger.error("Claude %s : erreur %s, %s (requête %s)", model, error.status_code, error.message, error.request_id)
        return None
    except anthropic.APIConnectionError as error:  # délai dépassé compris
        logger.warning("Claude %s injoignable : %s", model, error)
        return None
    if response.stop_reason == "refusal":
        category = response.stop_details.category if response.stop_details else None
        logger.warning("Claude %s a décliné la demande (%s).", model, category)
        return None
    if response.stop_reason == "max_tokens":
        logger.error("Claude %s : réponse tronquée à %s jetons.", model, max_tokens)
        return None
    text = next((block.text for block in response.content if block.type == "text"), "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Claude %s : JSON illisible (requête %s).", model, response._request_id)
        return None
