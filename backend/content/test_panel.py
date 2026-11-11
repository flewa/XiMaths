from datetime import timedelta

from django.utils import timezone

from gamification.services import balance

from .models import Message, Solution
from .tests import TL, ContentTestCase, Verdict, make_user


class PanelTests(ContentTestCase):
    """Panneau d'administration : réservé aux administrateurs, il montre tout sans rien décider."""

    def setUp(self):
        super().setUp()
        # Administrateur sans niveau de relecteur : il n'est pas tiré au sort pour relire.
        self.admin = make_user("admin", is_staff=True)
        self.moderator = make_user("moderatrice", trust=TL.MODERATOR, level=None)

    def get(self, path, user=None):
        self.client.force_login(user or self.admin)
        return self.client.get(f"/api/panel/{path}")

    def test_only_administrators_open_the_panel(self):
        for path in ["overview", "solutions", "members", "exercises"]:
            self.assertEqual(self.get(path, self.student).status_code, 403, path)
            # Une modératrice modère ; elle n'administre pas.
            self.assertEqual(self.get(path, self.moderator).status_code, 403, path)
            self.assertEqual(self.get(path).status_code, 200, path)
        self.client.logout()
        self.assertEqual(self.client.get("/api/panel/overview").status_code, 401)

    def test_overview_counts_copies_by_status_and_the_late_ones(self):
        validated = self.publish()
        self.validate(validated)
        late = self.publish(author=make_user("yanis", level="L1"))
        Solution.objects.filter(pk=late.pk).update(updated_at=timezone.now() - timedelta(hours=80))
        Message.objects.create(exercise=self.exercise, author=self.student, body="Une question")

        data = self.get("overview").json()
        self.assertEqual((data["under_review"], data["validated"], data["late"]), (1, 1, 1))
        self.assertEqual((data["exercises"], data["solutions_week"], data["messages_week"]), (1, 2, 1))
        self.assertEqual(data["reviews_week"], 3)
        self.assertEqual(len(data["days"]), 14)
        self.assertEqual(data["days"][-1]["solutions"], 2)
        # Les trois relecteurs, plus la modératrice ; l'administrateur sans niveau n'en est pas.
        self.assertGreaterEqual(data["reviewers"], 3)

    def test_copies_show_their_reviews_points_and_filters(self):
        validated = self.publish()
        self.validate(validated)
        other = make_user("yanis", level="L1")
        pending = self.publish(author=other)
        self.review(pending, pending.reviews.first().reviewer, Verdict.INCORRECT)

        page = self.get("solutions").json()
        self.assertEqual((page["total"], page["page"], page["pages"]), (2, 1, 1))
        by_id = {item["id"]: item for item in page["items"]}
        done = by_id[validated.pk]
        self.assertEqual((done["status"], done["author"], done["reviews_done"]), ("validated", "lea", 3))
        self.assertEqual(done["points"], balance(self.student))
        self.assertGreater(done["points"], 0)
        self.assertEqual({review["verdict"] for review in done["reviews"]}, {"correcte"})
        self.assertFalse(done["can_take"])

        waiting = by_id[pending.pk]
        self.assertEqual((waiting["reviews_done"], waiting["reviews_expected"], waiting["points"]), (1, 3, 0))
        self.assertTrue(waiting["can_take"])
        self.assertEqual(waiting["waiting_hours"], 0)

        self.assertEqual([item["id"] for item in self.get("solutions?status=under_review").json()["items"]], [pending.pk])
        self.assertEqual([item["id"] for item in self.get("solutions?status=validated").json()["items"]], [validated.pk])
        self.assertEqual(self.get("solutions?status=late").json()["total"], 0)
        self.assertEqual([item["id"] for item in self.get("solutions?q=yanis").json()["items"]], [pending.pk])
        self.assertEqual(self.get("solutions?q=Riemann").json()["total"], 2)
        self.assertEqual(self.get("solutions?status=n-importe-quoi").status_code, 422)

    def test_members_and_exercises_lists(self):
        self.validate(self.publish())
        members = self.get("members").json()
        lea = next(item for item in members["items"] if item["username"] == "lea")
        self.assertEqual((lea["solutions"], lea["validated"], lea["points"]), (1, 1, balance(self.student)))
        reviewer = next(item for item in members["items"] if item["username"] == "relecteur0")
        self.assertEqual(reviewer["reviews"], 1)
        # Aucune adresse email ne sort du panneau.
        self.assertNotIn("example.com", str(members))
        self.assertEqual({item["username"] for item in self.get("members?show=team").json()["items"]}, {"admin", "moderatrice"})
        self.assertEqual(self.get("members?q=relecteur").json()["total"], 3)

        [exercise] = self.get("exercises").json()["items"]
        self.assertEqual((exercise["solutions"], exercise["validated"], exercise["under_review"]), (1, 1, 0))
        self.assertEqual(self.get("exercises?status=unsolved").json()["total"], 0)
        self.assertEqual(self.get("exercises?status=draft").json()["total"], 0)

    def test_pages_hold_thirty_rows(self):
        for index in range(31):
            make_user(f"membre{index}", level=None)
        first = self.get("members").json()
        self.assertEqual((first["pages"], len(first["items"])), (2, 30))
        self.assertEqual(len(self.get("members?page=2").json()["items"]), first["total"] - 30)
        # Une page trop grande ramène à la dernière.
        self.assertEqual(self.get("members?page=99").json()["page"], 2)
