"""Doublons et LLM (facultatif, voir config/llm.py).

- E2 : Claude Haiku reformule chaque énoncé publié en deux ou trois phrases sans
  notation ; l'embedding de ce résumé rattrape les reformulations complètes.
- Arbitrage : Claude Sonnet donne son avis sur les paires « quasi-copie » et « très
  similaire », avec une justification d'une phrase. L'avis est mis en cache sur la
  paire ; un humain tranche toujours.
"""

from django.utils import timezone

from config import llm

from .embeddings import embed
from .models import DuplicatePair, Fingerprint

Relation = DuplicatePair.Relation
ARBITRATED_BANDS = (DuplicatePair.Band.QUASI_COPY, DuplicatePair.Band.VERY_SIMILAR)
BATCH = 50

SUMMARY_SYSTEM = (
    "Tu reformules des énoncés d'exercices de mathématiques du supérieur pour une détection "
    "de doublons. Écris deux ou trois phrases en français, sans aucune notation mathématique "
    "ni formule : les objets en jeu, les hypothèses, et la conclusion demandée. Deux énoncés "
    "qui demandent la même chose avec d'autres notations doivent donner le même résumé ; "
    "garde les valeurs numériques qui changent le problème."
)
SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {"summary": {"type": "string"}},
    "required": ["summary"],
    "additionalProperties": False,
}

ARBITRATION_SYSTEM = (
    "Tu compares deux énoncés d'exercices de mathématiques du supérieur publiés sur une "
    "plateforme communautaire, pour aider un modérateur à repérer les doublons. Le premier "
    "est le nouvel exercice, le second l'exercice existant. Qualifie la relation du nouvel "
    "exercice à l'existant :\n"
    "- identique : même problème, à la notation ou à la formulation près ;\n"
    "- variante_parametrique : même problème où seules des constantes changent ;\n"
    "- cas_particulier : le nouvel exercice est un cas particulier de l'existant ;\n"
    "- generalisation : le nouvel exercice généralise l'existant ;\n"
    "- meme_theme_distinct : même sujet, mais un autre problème ;\n"
    "- different : sans rapport réel.\n"
    "Changer une valeur, une hypothèse ou la conclusion rend deux exercices différents : "
    "ce n'est alors pas « identique ». Donne ta confiance entre 0 et 1, et une justification "
    "d'une phrase, en français, lisible par l'auteur de l'exercice."
)
ARBITRATION_SCHEMA = {
    "type": "object",
    "properties": {
        "relation": {"type": "string", "enum": [choice.value for choice in Relation]},
        "confidence": {"type": "number"},
        "rationale": {"type": "string"},
    },
    "required": ["relation", "confidence", "rationale"],
    "additionalProperties": False,
}


def summarize(statement):
    """Résumé canonique d'un énoncé, ou None."""
    answer = llm.ask_json(
        llm.SUMMARY_MODEL,
        system=SUMMARY_SYSTEM,
        prompt=f"Énoncé :\n\n{statement}",
        schema=SUMMARY_SCHEMA,
        effort="low",
        max_tokens=4000,
    )
    summary = (answer or {}).get("summary", "").strip()
    return summary or None


def index_summaries(limit=BATCH):
    """Résumés canoniques et embeddings E2 manquants. Il faut le LLM et le service
    d'embeddings. Renvoie le nombre d'énoncés traités."""
    if not llm.enabled():
        return 0
    done = 0
    for fingerprint in Fingerprint.objects.filter(summary="", embedding__isnull=False).select_related("exercise")[
        :limit
    ]:
        summary = summarize(fingerprint.exercise.statement)
        vector = embed(summary) if summary else None
        if vector is None:
            continue
        fingerprint.summary = summary
        fingerprint.summary_embedding = vector
        fingerprint.save(update_fields=["summary", "summary_embedding", "updated_at"])
        done += 1
    return done


def arbitrate(pair):
    """Avis du LLM sur une paire, mis en cache. Renvoie la paire, avis compris si obtenu."""
    answer = llm.ask_json(
        llm.ARBITRATION_MODEL,
        system=ARBITRATION_SYSTEM,
        prompt=(
            f"Nouvel exercice « {pair.exercise.title} » :\n\n{pair.exercise.statement}\n\n"
            f"---\n\nExercice existant « {pair.existing.title} » :\n\n{pair.existing.statement}"
        ),
        schema=ARBITRATION_SCHEMA,
        effort="high",
    )
    if answer and answer.get("relation") in Relation.values:
        pair.llm_relation = answer["relation"]
        pair.llm_confidence = min(1.0, max(0.0, float(answer.get("confidence", 0))))
        pair.llm_rationale = answer.get("rationale", "").strip()[:400]
        pair.llm_at = timezone.now()
        pair.save(update_fields=["llm_relation", "llm_confidence", "llm_rationale", "llm_at"])
    return pair


def arbitrate_pending(limit=BATCH):
    """Avis manquants sur les paires à arbitrer des bandes hautes. Renvoie leur nombre."""
    if not llm.enabled():
        return 0
    pending = DuplicatePair.objects.filter(
        status=DuplicatePair.Status.PENDING, band__in=ARBITRATED_BANDS, llm_relation=""
    ).select_related("exercise", "existing")[:limit]
    return sum(1 for pair in pending if arbitrate(pair).llm_relation)
