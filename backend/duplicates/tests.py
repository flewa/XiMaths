from unittest import mock

from django.core.exceptions import PermissionDenied
from django.test import SimpleTestCase
from django.utils import timezone

from catalog.models import Level
from config.errors import RuleError
from content.models import Exercise
from content.services import publish_exercise
from content.tests import ContentTestCase, make_user

from .embeddings import DIMENSIONS
from .minhash import signature, similarity
from .models import DuplicatePair, Fingerprint
from .normalize import normalize
from .services import (
    DuplicateSuspected,
    classify,
    compute_prints,
    decide,
    find_similar,
    index_exercise,
    publish_checked,
    scan,
    unmerge,
    variants_of,
)

Band = DuplicatePair.Band
Status = DuplicatePair.Status

SERIES = r"Montrer que la série $\sum_{n \geq 1} \frac{1}{n^2}$ converge, puis donner un majorant de sa somme."
# Même exercice, autres notations et autre nom de variable.
SERIES_REWRITTEN = (
    r"Démontrer que la série $$\displaystyle\sum_{k \geqslant 1} \dfrac{1}{k^2}$$ converge, "
    r"puis donner un majorant de sa somme."
)
# Variante paramétrique : seul l'exposant change.
SERIES_CUBES = r"Montrer que la série $\sum_{n \geq 1} \frac{1}{n^3}$ converge, puis donner un majorant de sa somme."
UNRELATED = r"Soit $A \in \mathcal{M}_n(\R)$ nilpotente. Montrer que $I_n - A$ est inversible."


def alpha(text):
    return normalize(text).alpha


class NormalizationTests(SimpleTestCase):
    def test_notation_synonyms_are_unified(self):
        self.assertEqual(
            alpha(r"Pour $x \in \R$, on a $x \leqslant \dfrac{1}{2}$."),
            alpha(r"Pour $x ∈ \mathbb{R}$, on a $x \le \frac12$."),
        )

    def test_spacing_and_sizing_commands_are_ignored(self):
        self.assertEqual(
            alpha(r"$\left( \displaystyle\int_0^1 f \right)^2$"),
            alpha(r"$(\int_0^1 f)^2$"),
        )

    def test_display_environments_are_equivalent(self):
        expected = alpha(r"On pose $$u_n = 2^n.$$")
        self.assertEqual(alpha(r"On pose \[u_n = 2^n.\]"), expected)
        self.assertEqual(alpha(r"On pose \begin{equation*}u_n = 2^n.\end{equation*}"), expected)
        # Le point final peut être dans la formule ou après.
        self.assertEqual(alpha(r"On pose $u_n = 2^n$."), expected)

    def test_variables_are_renamed_in_order_of_appearance(self):
        self.assertEqual(
            alpha(r"Soit $f$ continue. Montrer que $f(x) \geq x$."),
            alpha(r"Soit $g$ continue. Montrer que $g(t) \geq t$."),
        )
        self.assertEqual(alpha(r"$f(x) = x$"), ("F1", "(", "V1", ")", "=", "V1"))

    def test_named_operators_are_not_variables(self):
        self.assertIn("\\oprg", alpha(r"$\operatorname{rg}(A) = 2$"))

    def test_starters_are_normalized(self):
        self.assertEqual(alpha("Prouver que $x = 1$."), alpha("Montrer que $x = 1$."))
        self.assertEqual(alpha("Démontrer que $x = 1$."), alpha("Montrer que $x = 1$."))

    def test_abstract_version_hides_constants(self):
        self.assertEqual(normalize(SERIES).abstract, normalize(SERIES_CUBES).abstract)
        self.assertNotEqual(normalize(SERIES).alpha, normalize(SERIES_CUBES).alpha)

    def test_symbols_keep_their_meaning(self):
        self.assertIn("≠", alpha("On suppose $x \\neq 0$, soit x ≠ 0."))


class SignatureTests(SimpleTestCase):
    def jaccard(self, first, second, version="alpha"):
        return similarity(
            signature(getattr(normalize(first), version)), signature(getattr(normalize(second), version))
        )

    def test_a_rewritten_statement_is_a_quasi_copy(self):
        self.assertEqual(self.jaccard(SERIES, SERIES_REWRITTEN), 1)

    def test_a_parametric_variant_only_matches_in_the_abstract_version(self):
        self.assertLess(self.jaccard(SERIES, SERIES_CUBES), 0.85)
        self.assertEqual(self.jaccard(SERIES, SERIES_CUBES, "abstract"), 1)

    def test_unrelated_statements_share_nothing(self):
        self.assertLess(self.jaccard(SERIES, UNRELATED), 0.1)


class ClassificationTests(SimpleTestCase):
    def test_bands(self):
        self.assertEqual(classify(1.0, 1.0, None), Band.QUASI_COPY)
        self.assertEqual(classify(0.9, 0.95, None), Band.QUASI_COPY)
        # Seules les constantes changent : variante, même pour un long énoncé.
        self.assertEqual(classify(0.9, 1.0, None), Band.VARIANT)
        self.assertEqual(classify(0.5, 0.9, 0.95), Band.VARIANT)
        self.assertEqual(classify(0.5, 0.5, 0.9), Band.VERY_SIMILAR)
        self.assertEqual(classify(0.5, 0.5, 0.85), Band.MAYBE_RELATED)
        self.assertIsNone(classify(0.5, 0.5, 0.7))
        self.assertIsNone(classify(0.5, 0.5, None))


def same_vector(text):
    """Embedding factice : tous les énoncés sont sémantiquement identiques."""
    return [1.0] + [0.0] * (DIMENSIONS - 1)


@mock.patch("duplicates.services.embed", return_value=None)
class DetectionTests(ContentTestCase):
    def published(self, statement, *, author=None, title="Exercice"):
        exercise = Exercise.objects.create(
            author=author or self.author,
            title=title,
            statement=statement,
            difficulty_declared=2,
            primary_level=Level.objects.get(code="L1"),
        )
        publish_exercise(exercise)
        index_exercise(exercise)
        return exercise

    def draft(self, statement, *, author=None):
        return Exercise.objects.create(
            author=author or self.student,
            title="Brouillon",
            statement=statement,
            difficulty_declared=2,
            primary_level=Level.objects.get(code="L1"),
        )

    def test_a_quasi_copy_is_found_despite_other_notations(self, embed):
        existing = self.published(SERIES)
        self.published(UNRELATED)

        matches = find_similar(compute_prints(SERIES_REWRITTEN))

        self.assertEqual([(m.exercise, m.band) for m in matches], [(existing, Band.QUASI_COPY)])
        self.assertIsNone(matches[0].score)

    def test_a_parametric_variant_is_proposed_as_such(self, embed):
        existing = self.published(SERIES)
        [match] = find_similar(compute_prints(SERIES_CUBES))
        self.assertEqual((match.exercise, match.band), (existing, Band.VARIANT))

    def test_drafts_and_removed_exercises_are_ignored(self, embed):
        removed = self.published(SERIES)
        Exercise.objects.filter(pk=removed.pk).update(status=Exercise.Status.REMOVED)
        self.assertEqual(find_similar(compute_prints(SERIES)), [])

    def test_embeddings_catch_reformulations(self, embed):
        embed.side_effect = same_vector
        existing = self.published(SERIES)
        stored = Fingerprint.objects.get(pk=existing.pk).embedding
        self.assertEqual(stored.shape, (DIMENSIONS,))

        # Aucun mot en commun : seul le plus proche voisin sur E1 le trouve.
        [match] = find_similar(compute_prints("Établir la sommabilité de la famille des inverses des carrés."))

        self.assertEqual(match.exercise, existing)
        self.assertAlmostEqual(match.cosine, 1.0)
        self.assertEqual(match.band, Band.MAYBE_RELATED)

    def test_publishing_a_close_exercise_asks_the_author(self, embed):
        existing = self.published(SERIES)
        draft = self.draft(SERIES_REWRITTEN)

        with self.assertRaises(DuplicateSuspected) as raised:
            publish_checked(draft)

        self.assertEqual([m.exercise for m in raised.exception.matches], [existing])
        draft.refresh_from_db()
        self.assertEqual(draft.status, Exercise.Status.DRAFT)

    def test_different_publishes_and_queues_the_pair(self, embed):
        existing = self.published(SERIES)
        draft = self.draft(SERIES_REWRITTEN)

        publish_checked(draft, choice="different", note="On demande aussi la valeur exacte.")

        self.assertEqual(draft.status, Exercise.Status.PUBLISHED)
        pair = DuplicatePair.objects.get()
        self.assertEqual((pair.exercise, pair.existing, pair.status), (draft, existing, Status.PENDING))
        self.assertEqual(pair.author_note, "On demande aussi la valeur exacte.")
        self.assertTrue(hasattr(draft, "fingerprint"))

    def test_variant_publishes_linked_to_the_existing_exercise(self, embed):
        existing = self.published(SERIES)
        draft = self.draft(SERIES_CUBES)

        publish_checked(draft, choice="variante", target_id=existing.pk)

        self.assertEqual(list(variants_of(existing)), [draft])
        self.assertEqual(list(variants_of(draft)), [existing])
        self.assertEqual(DuplicatePair.objects.get().status, Status.VARIANTS)

    def test_the_variant_target_must_be_a_candidate(self, embed):
        self.published(SERIES)
        unrelated = self.published(UNRELATED)
        with self.assertRaises(RuleError):
            publish_checked(self.draft(SERIES_CUBES), choice="variante", target_id=unrelated.pk)

    def test_scan_opens_each_pair_once(self, embed):
        older = self.published(SERIES)
        newer = self.published(SERIES_REWRITTEN)

        self.assertEqual(scan(Exercise.objects.all()), 1)
        self.assertEqual(scan(Exercise.objects.all()), 0)

        pair = DuplicatePair.objects.get()
        self.assertEqual((pair.exercise, pair.existing, pair.author_choice), (newer, older, ""))

    def test_a_pair_declared_distinct_is_never_proposed_again(self, embed):
        older = self.published(SERIES)
        newer = self.published(SERIES_REWRITTEN)
        scan([newer])

        decide(DuplicatePair.objects.get(), Status.DISTINCT, make_user("modo", is_staff=True))

        self.assertEqual(find_similar(compute_prints(newer.statement), exercise=newer), [])
        self.assertEqual(find_similar(compute_prints(older.statement), exercise=older), [])
        self.assertEqual(scan(Exercise.objects.all()), 0)

    def test_the_admin_queue_shows_pairs_and_applies_decisions(self, embed):
        self.published(SERIES)
        scan([self.published(SERIES_REWRITTEN)])
        pair = DuplicatePair.objects.get()
        self.client.force_login(make_user("modo", is_staff=True, is_superuser=True))

        self.assertContains(self.client.get("/admin/duplicates/duplicatepair/"), "Quasi-copie")
        change_page = self.client.get(f"/admin/duplicates/duplicatepair/{pair.pk}/change/")
        self.assertContains(change_page, "Énoncés côte à côte")
        self.client.post(
            "/admin/duplicates/duplicatepair/",
            {"action": "declare_distinct", "_selected_action": [pair.pk]},
        )

        pair.refresh_from_db()
        self.assertEqual(pair.status, Status.DISTINCT)

    def test_only_moderators_decide(self, embed):
        self.published(SERIES)
        scan([self.published(SERIES_REWRITTEN)])
        with self.assertRaises(PermissionDenied):
            decide(DuplicatePair.objects.get(), Status.MERGED, self.student)

    def test_a_merge_moves_solutions_and_can_be_undone(self, embed):
        older = self.published(SERIES)
        newer = self.published(SERIES_REWRITTEN)
        solution = self.publish(exercise=newer)
        scan([newer])
        pair = DuplicatePair.objects.get()
        moderator = make_user("modo", is_staff=True)

        decide(pair, Status.MERGED, moderator)

        newer.refresh_from_db()
        solution.refresh_from_db()
        self.assertEqual((newer.status, newer.merged_into), (Exercise.Status.MERGED, older))
        self.assertEqual(solution.exercise, older)
        detail = self.client.get(f"/api/exercises/{newer.pk}").json()
        self.assertEqual(detail["merged_into"], older.pk)
        self.assertNotIn(newer.pk, [e["id"] for e in self.client.get("/api/exercises").json()])
        with self.assertRaises(RuleError):
            decide(pair, Status.DISTINCT, moderator)

        unmerge(pair, moderator)

        newer.refresh_from_db()
        solution.refresh_from_db()
        self.assertEqual((newer.status, newer.merged_into), (Exercise.Status.PUBLISHED, None))
        self.assertEqual(solution.exercise, newer)
        self.assertEqual((pair.status, pair.decided_by), (Status.PENDING, None))


@mock.patch("duplicates.services.embed", return_value=None)
class DuplicateApiTests(ContentTestCase):
    """API : panneau « Exercices proches » et publication avec choix de l'auteur."""

    def setUp(self):
        super().setUp()
        for user in (self.author, self.student):
            user.email_verified_at = timezone.now()
            user.save()
        self.client.force_login(self.student)

    def post(self, url, data=None):
        return self.client.post(url, data or {}, content_type="application/json")

    def create_draft(self, statement):
        response = self.post(
            "/api/exercises",
            {"title": "Ma série", "statement": statement, "difficulty": 2, "primary_level": "L1"},
        )
        return response.json()["id"]

    def existing(self):
        exercise = Exercise.objects.create(
            author=self.author,
            title="Série des inverses des carrés",
            statement=SERIES,
            difficulty_declared=2,
            primary_level=Level.objects.get(code="L1"),
        )
        publish_exercise(exercise)
        index_exercise(exercise)
        return exercise

    def test_similar_lists_close_exercises_while_writing(self, embed):
        existing = self.existing()

        response = self.post("/api/exercises/similar", {"statement": SERIES_REWRITTEN})

        self.assertEqual(response.status_code, 200)
        [candidate] = response.json()
        self.assertEqual(candidate["id"], existing.pk)
        self.assertEqual(candidate["band_label"], "Quasi-copie")
        self.assertEqual(candidate["validated_solutions"], 0)

    def test_similar_requires_a_contributor(self, embed):
        self.client.logout()
        self.assertEqual(self.post("/api/exercises/similar", {"statement": SERIES}).status_code, 401)

    def test_publish_answers_409_then_accepts_the_authors_choice(self, embed):
        existing = self.existing()
        draft_id = self.create_draft(SERIES_REWRITTEN)

        response = self.post(f"/api/exercises/{draft_id}/publish")
        self.assertEqual(response.status_code, 409)
        self.assertEqual([c["id"] for c in response.json()["candidates"]], [existing.pk])

        # « C'est différent » demande une phrase d'explication.
        response = self.post(f"/api/exercises/{draft_id}/publish", {"choice": "different"})
        self.assertEqual(response.status_code, 422)

        response = self.post(
            f"/api/exercises/{draft_id}/publish",
            {"choice": "different", "note": "Ici on demande un majorant explicite."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DuplicatePair.objects.get().status, Status.PENDING)

    def test_a_variant_shows_on_both_exercises(self, embed):
        existing = self.existing()
        draft_id = self.create_draft(SERIES_CUBES)

        response = self.post(
            f"/api/exercises/{draft_id}/publish", {"choice": "variante", "target_id": existing.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["variants"], [{"id": existing.pk, "title": existing.title}])
        detail = self.client.get(f"/api/exercises/{existing.pk}").json()
        self.assertEqual(detail["variants"], [{"id": draft_id, "title": "Ma série"}])

    def test_a_draft_can_be_edited_by_its_author_only(self, embed):
        draft_id = self.create_draft(SERIES)
        payload = {"title": "Ma série", "statement": UNRELATED, "difficulty": 3, "primary_level": "L2"}

        response = self.client.put(f"/api/exercises/{draft_id}", payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        draft = Exercise.objects.get(pk=draft_id)
        self.assertEqual((draft.statement, draft.difficulty_declared), (UNRELATED, 3))

        self.client.force_login(self.author)
        response = self.client.put(f"/api/exercises/{draft_id}", payload, content_type="application/json")
        self.assertEqual(response.status_code, 404)
