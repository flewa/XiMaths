"""Notions (sous-chapitres) : pages d'entrée, exercices proches, import de la rédaction."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from catalog.models import Level, Topic
from gamification.skills import skills_map

from .editorial import EXERCISES
from .management.commands.import_exercises import EDITORIAL_USERNAME, problems
from .models import Exercise
from .services import publish_exercise
from .tests import ContentTestCase, make_user


def topic(slug):
    return Topic.objects.get(slug=slug)


class NotionCatalogTests(TestCase):
    def test_every_notion_sits_under_one_of_the_seven_chapters(self):
        chapters = set(Topic.objects.filter(parent=None).values_list("slug", flat=True))
        self.assertEqual(
            chapters,
            {"algebre", "algebre-lineaire", "analyse", "arithmetique", "geometrie", "probabilites", "topologie"},
        )
        notions = Topic.objects.exclude(parent=None)
        self.assertGreaterEqual(notions.count(), 30)
        self.assertTrue(all(notion.parent.parent_id is None for notion in notions))

    def test_the_topics_api_gives_the_parent_and_the_published_count(self):
        response = self.client.get("/api/topics").json()
        by_slug = {item["slug"]: item for item in response}
        self.assertIsNone(by_slug["analyse"]["parent"])
        self.assertEqual(by_slug["series-entieres"]["parent"], "analyse")
        self.assertEqual(by_slug["series-entieres"]["exercises"], 0)


class NotionTaggingTests(ContentTestCase):
    def create(self, title, slugs, level="L2", **fields):
        exercise = Exercise.objects.create(
            author=self.author,
            title=title,
            statement=f"Énoncé propre à « {title} », pour ne pas passer pour un doublon.",
            difficulty_declared=2,
            primary_level=Level.objects.get(code=level),
            **fields,
        )
        exercise.topics.set(Topic.objects.filter(slug__in=slugs))
        return publish_exercise(exercise)

    def test_choosing_a_notion_files_the_exercise_under_its_chapter_too(self):
        user = make_user("autrice", email_verified_at=timezone.now())
        self.client.force_login(user)
        payload = {
            "title": "Rayon de convergence",
            "statement": "Déterminer le rayon de convergence de $\\sum n x^n$.",
            "difficulty": 2,
            "primary_level": "L2",
            "topics": ["series-entieres"],
        }
        response = self.client.post("/api/exercises", payload, content_type="application/json")
        self.assertEqual(response.status_code, 201, response.content)
        exercise = Exercise.objects.get(pk=response.json()["id"])
        self.assertEqual(set(exercise.topics.values_list("slug", flat=True)), {"series-entieres", "analyse"})

    def test_summaries_separate_chapters_and_notions_and_filter_by_notion(self):
        self.create("Série entière A", ["analyse", "series-entieres"])
        self.create("Intégrale B", ["analyse", "calcul-integral"])

        items = self.client.get("/api/exercises?topic=series-entieres").json()

        self.assertEqual([item["title"] for item in items], ["Série entière A"])
        self.assertEqual((items[0]["topics"], items[0]["notions"]), (["Analyse"], ["Séries entières"]))
        counts = {item["slug"]: item["exercises"] for item in self.client.get("/api/topics").json()}
        self.assertEqual((counts["series-entieres"], counts["calcul-integral"]), (1, 1))

    def test_related_exercises_share_the_notion_first_then_the_chapter(self):
        base = self.create("Base", ["analyse", "series-entieres"])
        same_notion = self.create("Même notion", ["analyse", "series-entieres"], level="MP")
        same_chapter_level = self.create("Même chapitre", ["analyse", "calcul-integral"])
        self.create("Autre chapitre", ["probabilites"])

        related = self.client.get(f"/api/exercises/{base.pk}/related").json()

        # Ni l'exercice lui-même, ni celui d'un autre chapitre ; la notion avant le niveau.
        self.assertEqual([item["id"] for item in related], [same_notion.pk, same_chapter_level.pk])

    def test_an_exercise_without_chapter_has_no_related_exercises(self):
        self.assertEqual(self.client.get(f"/api/exercises/{self.exercise.pk}/related").json(), [])
        self.assertEqual(self.client.get("/api/exercises/999999/related").status_code, 404)

    def test_the_skills_map_stays_by_chapter(self):
        names = {entry["topic"].slug for entry in skills_map(self.student)}
        self.assertEqual(names, set(Topic.objects.filter(parent=None).values_list("slug", flat=True)))


def run(*args):
    out = StringIO()
    call_command("import_exercises", *args, stdout=out)
    return out.getvalue()


class EditorialNotionTests(TestCase):
    def test_every_editorial_exercise_has_a_notion(self):
        notions = set(Topic.objects.exclude(parent=None).values_list("slug", flat=True))
        bare = [spec["title"] for spec in EXERCISES if not notions & set(spec["topics"])]
        self.assertEqual(bare, [])

    def test_a_former_title_cannot_be_reused(self):
        clash = [EXERCISES[0], {**EXERCISES[1], "former_titles": [EXERCISES[0]["title"]]}]
        self.assertTrue(any("ancien titre" in line for line in problems(clash)))

    def test_the_import_renames_and_retags_what_it_already_published(self):
        run()
        renamed = next(spec for spec in EXERCISES if spec.get("former_titles"))
        exercise = Exercise.objects.get(author__username=EDITORIAL_USERNAME, title=renamed["title"])
        Exercise.objects.filter(pk=exercise.pk).update(title=renamed["former_titles"][0])
        exercise.topics.set([topic("analyse")])

        output = run()

        self.assertIn(f"Déjà là : {len(EXERCISES)}. Mis à jour : 1.", output)
        exercise.refresh_from_db()
        self.assertEqual(exercise.title, renamed["title"])
        notion_slugs = set(exercise.topics.values_list("slug", flat=True))
        self.assertEqual(notion_slugs, set(renamed["topics"]) | {topic(s).parent.slug for s in renamed["topics"] if topic(s).parent})
        self.assertEqual(Exercise.objects.count(), len(EXERCISES))
