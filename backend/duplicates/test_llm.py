from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import TestCase, override_settings

from config import llm
from content.models import Exercise
from content.tests import ContentTestCase

from . import llm as duplicates_llm
from .models import DuplicatePair, Fingerprint
from .services import index_exercise, scan


def unit(*values):
    vector = np.zeros(1024)
    vector[: len(values)] = values
    return list(vector / np.linalg.norm(vector))


def response(text, stop_reason="end_turn"):
    return SimpleNamespace(
        stop_reason=stop_reason,
        stop_details=None,
        content=[SimpleNamespace(type="text", text=text)],
        _request_id="req_test",
    )


class AskJsonTests(TestCase):
    def test_nothing_is_called_without_a_key(self):
        with mock.patch.object(llm, "_client") as client:
            self.assertIsNone(llm.ask_json(llm.SUMMARY_MODEL, system="", prompt="", schema={}, effort="low"))
        client.assert_not_called()

    @override_settings(ANTHROPIC_API_KEY="test")
    def test_json_and_refusals(self):
        client = mock.Mock()
        client.messages.create.return_value = response('{"summary": "Une série."}')
        client.beta.messages.create.return_value = response("", stop_reason="refusal")
        with mock.patch.object(llm, "_client", return_value=client):
            summary = llm.ask_json(llm.SUMMARY_MODEL, system="s", prompt="p", schema={}, effort="low")
            refused = llm.ask_json(llm.ARBITRATION_MODEL, system="s", prompt="p", schema={}, effort="high")

        self.assertEqual(summary, {"summary": "Une série."})
        self.assertIsNone(refused)
        # Haiku sans repli côté serveur ; Sonnet avec le repli recommandé.
        self.assertNotIn("fallbacks", client.messages.create.call_args.kwargs)
        self.assertEqual(client.beta.messages.create.call_args.kwargs["fallbacks"], "default")


class DuplicateLlmTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        self.other = self.make_exercise()

    @override_settings(ANTHROPIC_API_KEY="test")
    def test_summaries_feed_the_e2_score(self):
        with mock.patch("duplicates.services.embed", return_value=unit(1, 0)):
            first = index_exercise(self.exercise)
        with mock.patch("duplicates.services.embed", return_value=unit(0.8, 0.6)):
            index_exercise(self.other)
        # E1 à 0,8, mais des résumés canoniques identiques.
        with (
            mock.patch.object(duplicates_llm, "summarize", return_value="Convergence de la série des inverses des carrés."),
            mock.patch.object(duplicates_llm, "embed", return_value=unit(0, 0, 1)),
        ):
            self.assertEqual(duplicates_llm.index_summaries(), 2)
        first.refresh_from_db()
        self.assertTrue(first.summary)

        # Comme la tâche nocturne : des empreintes relues en base, résumés compris.
        scan(Exercise.objects.filter(pk=self.other.pk).select_related("fingerprint"))
        pair = DuplicatePair.objects.get()
        # s = 0,45 cos(E1) + 0,35 cos(E2) + 0,20 J(F), avec des résumés identiques.
        self.assertAlmostEqual(pair.score, 0.45 * 0.8 + 0.35 * 1 + 0.20 * pair.jaccard, places=5)

    @override_settings(ANTHROPIC_API_KEY="test")
    def test_the_verdict_is_cached_on_the_pair(self):
        pair = DuplicatePair.objects.create(
            exercise=self.other, existing=self.exercise, band=DuplicatePair.Band.VERY_SIMILAR, jaccard=0.5, abstract_jaccard=0.5
        )
        verdict = {"relation": "identique", "confidence": 1.4, "rationale": "Même série, autre indice."}
        with mock.patch.object(llm, "ask_json", return_value=verdict) as ask:
            self.assertEqual(duplicates_llm.arbitrate_pending(), 1)
            self.assertEqual(duplicates_llm.arbitrate_pending(), 0)
        ask.assert_called_once()
        pair.refresh_from_db()
        self.assertEqual((pair.llm_relation, pair.llm_confidence), ("identique", 1.0))

    def test_without_a_key_nothing_is_arbitrated(self):
        DuplicatePair.objects.create(
            exercise=self.other, existing=self.exercise, band=DuplicatePair.Band.QUASI_COPY, jaccard=0.9, abstract_jaccard=0.9
        )
        self.assertEqual(duplicates_llm.arbitrate_pending(), 0)
        self.assertFalse(Fingerprint.objects.exclude(summary="").exists())
