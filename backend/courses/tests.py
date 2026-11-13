"""Rappels de cours : fichiers de la rédaction, import, et visibilité réservée à l'équipe
tant qu'un admin n'a pas publié la fiche."""

import re
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from catalog.models import Topic
from content.tests import make_user

from .models import CourseNote
from .services import import_sources
from .sources import load_sources, parse

NOTE = """---
titre: Séries entières
programmes: MP, PSI
ordre: 3
notion: series-entieres
---

## Rayon de convergence

Soit $(a_n)_{n \\in \\mathbb{N}}$ une suite complexe.
"""


def source(text=NOTE, slug="series-entieres", cycle="spe"):
    return parse(text, slug=slug, cycle=cycle)


class SourceTests(TestCase):
    def test_reads_the_header_and_keeps_the_body(self):
        note = source()
        self.assertEqual((note.title, note.programs, note.position, note.topic), ("Séries entières", "MP, PSI", 3, "series-entieres"))
        self.assertTrue(note.body.startswith("## Rayon de convergence"))

    def test_rejects_an_incomplete_or_unknown_header(self):
        for text, message in [
            ("## Sans en-tête", "en-tête"),
            ("---\ntitre: X\nprogrammes: MP\n---\nCorps", "ordre"),
            ("---\ntitre: X\nprogrammes: MP\nordre: 1\nauteur: moi\n---\nCorps", "auteur"),
            ("---\ntitre: X\nprogrammes: MP\nordre: un\n---\nCorps", "entier"),
            ("---\ntitre: X\nprogrammes: MP\nordre: 1\n---\n  \n", "vide"),
        ]:
            with self.subTest(message=message), self.assertRaisesMessage(ValueError, message):
                source(text)

    def test_two_files_with_the_same_name_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            for cycle in ("sup", "spe"):
                (Path(directory) / cycle).mkdir()
                (Path(directory) / cycle / "polynomes.md").write_text(NOTE)
            with self.assertRaisesMessage(ValueError, "double"):
                load_sources(Path(directory))


class EditorialNotesTests(TestCase):
    """Les fiches du dépôt : lisibles, rangées, rattachées à des notions du site."""

    def test_every_note_loads_and_points_to_a_known_topic(self):
        sources = load_sources()
        self.assertGreater(len(sources), 0)
        topics = set(Topic.objects.values_list("slug", flat=True))
        for note in sources:
            with self.subTest(note=note.slug):
                self.assertIn(note.topic, topics)
                self.assertEqual(note.body.count("$$") % 2, 0, "un bloc $$ n'est pas fermé")

    def test_positions_are_distinct_within_a_cycle(self):
        for cycle in ("sup", "spe"):
            positions = [note.position for note in load_sources() if note.cycle == cycle]
            self.assertEqual(len(positions), len(set(positions)), cycle)

    def test_notes_avoid_tables_the_site_does_not_render(self):
        # Le rendu du site (react-markdown sans GFM) n'affiche pas les tableaux Markdown.
        for note in load_sources():
            with self.subTest(note=note.slug):
                self.assertFalse(any(line.lstrip().startswith("|") for line in note.body.splitlines()))

    def test_a_minus_after_an_opening_bracket_is_unary(self):
        # « ]-r, r[ » : KaTeX lit le « - » comme une soustraction et l'écarte du crochet ;
        # on écrit « ]{-}r, r[ ».
        for note in load_sources():
            with self.subTest(note=note.slug):
                self.assertIsNone(re.search(r"\][ ]*-", note.body))

    def test_notes_only_use_the_macros_the_site_provides(self):
        # \newcommand et \def ne passent pas dans le rendu du site (voir MathMarkdown).
        for note in load_sources():
            with self.subTest(note=note.slug):
                self.assertIsNone(re.search(r"\\(newcommand|def|renewcommand)\b", note.body))


class ImportTests(TestCase):
    def test_import_creates_drafts_and_is_idempotent(self):
        self.assertEqual(import_sources([source()]), (1, 0, 0))
        note = CourseNote.objects.get(slug="series-entieres")
        self.assertFalse(note.published)
        self.assertEqual(note.topic.slug, "series-entieres")
        self.assertEqual(import_sources([source()]), (0, 0, 0))

    def test_a_changed_text_goes_back_to_draft(self):
        import_sources([source()])
        note = CourseNote.objects.get()
        note.published_at = note.updated_at
        note.save()
        self.assertEqual(import_sources([source(NOTE.replace("complexe", "de complexes"))]), (0, 1, 1))
        self.assertFalse(CourseNote.objects.get().published)

    def test_a_new_position_keeps_the_note_published(self):
        import_sources([source()])
        CourseNote.objects.update(published_at="2026-11-01T10:00:00Z")
        self.assertEqual(import_sources([source(NOTE.replace("ordre: 3", "ordre: 4"))]), (0, 1, 0))
        note = CourseNote.objects.get()
        self.assertTrue(note.published)
        self.assertEqual(note.position, 4)

    def test_an_unknown_topic_stops_the_import(self):
        with self.assertRaisesMessage(ValueError, "inconnues"):
            import_sources([source(NOTE.replace("notion: series-entieres", "notion: alchimie"))])
        self.assertFalse(CourseNote.objects.exists())

    def test_command_imports_the_editorial_notes(self):
        out = StringIO()
        call_command("import_course_notes", stdout=out)
        self.assertEqual(CourseNote.objects.count(), len(load_sources()))
        self.assertFalse(CourseNote.objects.filter(published_at__isnull=False).exists())
        self.assertIn("nouvelles", out.getvalue())


class ApiTests(TestCase):
    def setUp(self):
        import_sources([source(), source(NOTE.replace("Séries entières", "Polynômes"), slug="polynomes", cycle="sup")])
        self.admin = make_user("admin", is_staff=True, email_verified_at="2026-01-01T00:00:00Z")
        self.member = make_user("lea", email_verified_at="2026-01-01T00:00:00Z")

    def test_drafts_are_hidden_from_visitors_and_members(self):
        self.assertEqual(self.client.get("/api/course-notes").json(), [])
        self.assertEqual(self.client.get("/api/course-notes/polynomes").status_code, 404)
        self.client.force_login(self.member)
        self.assertEqual(self.client.get("/api/course-notes").json(), [])
        self.assertEqual(self.client.get("/api/course-notes/polynomes").status_code, 404)

    def test_staff_sees_drafts_and_publishes_them(self):
        self.client.force_login(self.admin)
        listed = self.client.get("/api/course-notes").json()
        self.assertEqual([(note["slug"], note["published"]) for note in listed], [("polynomes", False), ("series-entieres", False)])
        self.assertIn("Rayon de convergence", self.client.get("/api/course-notes/series-entieres").json()["body"])
        published = self.client.post("/api/course-notes/series-entieres/publish").json()
        self.assertTrue(published["published"])
        self.assertEqual(CourseNote.objects.get(slug="series-entieres").published_by, self.admin)

        self.client.logout()
        listed = self.client.get("/api/course-notes").json()
        self.assertEqual([note["slug"] for note in listed], ["series-entieres"])
        self.assertEqual(self.client.get("/api/course-notes?topic=series-entieres").json()[0]["topic_name"], "Séries entières")
        self.assertEqual(self.client.get("/api/course-notes?topic=polynomes").json(), [])
        self.assertEqual(self.client.get("/api/course-notes/series-entieres").status_code, 200)

    def test_unpublish_hides_the_note_again(self):
        self.client.force_login(self.admin)
        self.client.post("/api/course-notes/polynomes/publish")
        self.assertFalse(self.client.post("/api/course-notes/polynomes/unpublish").json()["published"])
        self.client.logout()
        self.assertEqual(self.client.get("/api/course-notes/polynomes").status_code, 404)

    def test_only_staff_may_publish(self):
        self.assertEqual(self.client.post("/api/course-notes/polynomes/publish").status_code, 401)
        self.client.force_login(self.member)
        self.assertEqual(self.client.post("/api/course-notes/polynomes/publish").status_code, 403)
        self.assertFalse(CourseNote.objects.get(slug="polynomes").published)

    def test_me_tells_the_site_who_is_staff(self):
        self.client.force_login(self.admin)
        self.assertTrue(self.client.get("/api/auth/me").json()["is_staff"])
        self.client.force_login(self.member)
        self.assertFalse(self.client.get("/api/auth/me").json()["is_staff"])
