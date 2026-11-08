"""Profil public : personnalisation, page d'un membre, avatars des classements."""

from django.test import TestCase
from django.utils import timezone

from catalog.models import Topic
from content.tests import ContentTestCase, make_user
from gamification.models import UserBadge

from .profile import AVATAR_COLORS, EDITORIAL_USERNAME, avatar_of, default_color


class AvatarTests(TestCase):
    def test_without_a_choice_the_avatar_is_stable_and_shows_the_initial(self):
        user = make_user("lea")
        self.assertEqual(avatar_of(user), {"color": default_color("lea"), "symbol": "L", "custom_symbol": False})
        self.assertIn(default_color("lea"), AVATAR_COLORS)
        self.assertEqual(default_color("Lea"), default_color("lea"))


class ProfileApiTests(TestCase):
    def setUp(self):
        self.user = make_user("lea", email_verified_at=timezone.now())
        UserBadge.objects.create(user=self.user, badge="premier-pas", awarded_at=timezone.now())
        self.client.force_login(self.user)

    def put(self, **fields):
        payload = {"bio": "", "avatar_color": "", "avatar_symbol": "", "featured_badges": [], "favorite_topics": [], **fields}
        return self.client.put("/api/auth/profile", payload, content_type="application/json")

    def test_a_member_customises_their_profile(self):
        response = self.put(
            bio="  En MPSI,   fan de topologie. ",
            avatar_color="jade",
            avatar_symbol="∫",
            featured_badges=["premier-pas"],
            favorite_topics=["topologie", "series-entieres"],
        )
        self.assertEqual(response.status_code, 200)
        me = response.json()
        self.assertEqual(me["bio"], "En MPSI, fan de topologie.")
        self.assertEqual(me["avatar"], {"color": "jade", "symbol": "∫", "custom_symbol": True})
        self.assertEqual(me["featured_badges"], ["premier-pas"])
        self.assertEqual(sorted(me["favorite_topics"]), ["series-entieres", "topologie"])

    def test_the_profile_refuses_links_unknown_choices_and_badges_not_owned(self):
        for fields, message in [
            ({"bio": "Mon site : https://exemple.com"}, "lien"),
            ({"bio": "x" * 201}, "200"),
            ({"avatar_color": "fluo"}, "Couleur"),
            ({"avatar_symbol": "☃"}, "Symbole"),
            ({"featured_badges": ["pionnier"]}, "obtenus"),
            ({"favorite_topics": ["alchimie"]}, "inconnu"),
            ({"favorite_topics": ["analyse", "algebre", "topologie", "probabilites"]}, "3 chapitres"),
        ]:
            with self.subTest(message=message):
                response = self.put(**fields)
                self.assertEqual(response.status_code, 422)
                self.assertIn(message, response.json()["detail"])

    def test_the_options_are_public(self):
        options = self.client.get("/api/auth/profile-options").json()
        self.assertIn("corail", options["colors"])
        self.assertIn("∑", options["symbols"])


class MemberPageTests(ContentTestCase):
    def test_the_member_page_shows_the_profile_but_no_solution(self):
        self.student.bio = "Je prépare les concours."
        self.student.avatar_color = "ciel"
        self.student.featured_badges = ["premier-pas", "pionnier"]
        self.student.save()
        self.student.favorite_topics.set(Topic.objects.filter(slug="analyse"))
        UserBadge.objects.create(user=self.student, badge="premier-pas", awarded_at=timezone.now())

        member = self.client.get("/api/members/lea").json()

        self.assertEqual(member["bio"], "Je prépare les concours.")
        self.assertEqual(member["avatar"]["color"], "ciel")
        # Un badge non obtenu n'apparaît pas dans la vitrine.
        self.assertEqual([badge["slug"] for badge in member["featured_badges"]], ["premier-pas"])
        self.assertEqual(member["favorite_topics"], [{"slug": "analyse", "name": "Analyse"}])
        self.assertFalse(member["is_me"])
        self.assertEqual(member["reviews_done"], 0)
        self.assertNotIn("solutions", member)

        author = self.client.get("/api/members/auteur").json()
        self.assertEqual([exercise["id"] for exercise in author["recent_exercises"]], [self.exercise.pk])

    def test_leaderboard_entries_carry_the_avatar_and_showcase(self):
        self.student.avatar_symbol = "π"
        self.student.featured_badges = ["premier-pas"]
        self.student.save()
        self.validate(self.publish())
        [entry] = [e for e in self.client.get("/api/leaderboards").json()["top"] if e["username"] == "lea"]
        self.assertEqual(entry["avatar"]["symbol"], "π")
        self.assertEqual(entry["featured_badges"], [{"slug": "premier-pas", "name": "Premier pas"}])

    def test_exercises_name_their_member_author_but_not_the_editorial_account(self):
        self.author.avatar_symbol = "∑"
        self.author.save()
        [listed] = [e for e in self.client.get("/api/exercises").json() if e["id"] == self.exercise.pk]
        self.assertEqual(listed["author_profile"]["username"], "auteur")
        self.assertEqual(listed["author_profile"]["avatar"]["symbol"], "∑")

        self.author.username = EDITORIAL_USERNAME
        self.author.save()
        detail = self.client.get(f"/api/exercises/{self.exercise.pk}").json()
        self.assertIsNone(detail["author_profile"])
        self.assertEqual(detail["author"], EDITORIAL_USERNAME)
