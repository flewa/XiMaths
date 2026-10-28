import re

from django.core import mail, signing
from django.core.cache import cache
from django.test import TestCase, override_settings

from content.tests import make_user
from gamification.models import UserBadge

from . import academic
from .services import delete_account, export_user_data
from .tests import post


class AcademicDomainTests(TestCase):
    def test_french_higher_education_domains_and_their_subdomains(self):
        for email in (
            "lea@etu.univ-lyon1.fr",
            "lea@univ-grenoble-alpes.fr",
            "lea@etu.u-paris.fr",
            "lea@universite-paris-saclay.fr",
            "lea@etu.unistra.fr",
            "lea@ens-lyon.fr",
            "lea@polytechnique.edu",
            "lea@ac-versailles.fr",
            "lea@dauphine.psl.eu",
        ):
            self.assertTrue(academic.is_academic(email), email)

    def test_other_domains_are_refused(self):
        for email in ("lea@gmail.com", "lea@unicef.fr", "lea@univ-lyon1.fr.example.com", "lea@etu.example.com"):
            self.assertFalse(academic.is_academic(email), email)

    @override_settings(ACADEMIC_EXTRA_DOMAINS=["ecole-exemple.fr"])
    def test_extra_domains_come_from_the_settings(self):
        self.assertTrue(academic.is_academic("lea@etud.ecole-exemple.fr"))


class AcademicApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.lea = make_user("lea")
        self.client.force_login(self.lea)

    def request(self, email):
        return post(self.client, "/api/auth/academic", {"email": email})

    def verify(self):
        token = re.search(r"academique=(\S+)", mail.outbox[-1].body).group(1)
        return post(self.client, "/api/auth/academic/verify", {"token": token})

    def test_the_link_confirms_the_address_and_awards_the_badge(self):
        self.assertEqual(self.request(" Lea.Martin@Etu.Univ-Lyon1.fr ").status_code, 204)
        self.assertEqual(mail.outbox[-1].to, ["lea.martin@etu.univ-lyon1.fr"])
        self.assertNotIn("lea.martin", mail.outbox[-1].body.split("academique=")[1])

        response = self.verify()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["academic_domain"], "etu.univ-lyon1.fr")
        self.lea.refresh_from_db()
        self.assertIsNotNone(self.lea.academic_verified_at)
        self.assertEqual(self.lea.academic_email_digest, academic.digest("lea.martin@etu.univ-lyon1.fr"))
        self.assertTrue(UserBadge.objects.filter(user=self.lea, badge="etudiant-verifie").exists())
        # Le lien sert encore sans rien changer.
        self.assertEqual(self.verify().status_code, 200)

    def test_a_non_academic_address_is_refused_without_email(self):
        response = self.request("lea@gmail.com")

        self.assertEqual(response.status_code, 422)
        self.assertIn("établissement", response.json()["detail"])
        self.assertEqual(mail.outbox, [])

    def test_one_academic_address_verifies_one_account(self):
        self.request("lea@etu.unistra.fr")
        self.verify()
        self.client.force_login(make_user("yanis"))

        response = self.request("LEA@etu.unistra.fr")

        self.assertEqual(response.status_code, 422)
        self.assertIn("autre compte", response.json()["detail"])

    def test_a_link_already_used_by_another_account_is_refused(self):
        self.request("lea@etu.unistra.fr")
        token = re.search(r"academique=(\S+)", mail.outbox[-1].body).group(1)
        yanis = make_user("yanis")
        yanis.academic_email_digest = academic.digest("lea@etu.unistra.fr")
        yanis.save()

        response = post(self.client, "/api/auth/academic/verify", {"token": token})

        self.assertEqual(response.status_code, 400)
        self.lea.refresh_from_db()
        self.assertIsNone(self.lea.academic_verified_at)

    def test_forged_and_expired_links_are_refused(self):
        forged = post(self.client, "/api/auth/academic/verify", {"token": "abc"})
        expired = signing.dumps({"uid": self.lea.pk, "digest": "x", "domain": "unistra.fr"}, salt="autre")

        self.assertEqual(forged.status_code, 400)
        self.assertEqual(post(self.client, "/api/auth/academic/verify", {"token": expired}).status_code, 400)

    def test_sending_needs_a_session(self):
        self.client.logout()
        self.assertEqual(self.request("lea@etu.unistra.fr").status_code, 401)

    def test_export_shows_the_domain_and_deletion_frees_the_address(self):
        self.request("lea@etu.unistra.fr")
        self.verify()
        self.lea.refresh_from_db()

        self.assertEqual(export_user_data(self.lea)["compte"]["email_academique"]["domaine"], "etu.unistra.fr")
        delete_account(self.lea)
        self.lea.refresh_from_db()
        self.assertEqual((self.lea.academic_verified_at, self.lea.academic_email_digest), (None, None))
