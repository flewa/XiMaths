"""Photos de copie envoyées depuis un téléphone (QR code), jointes aux solutions."""

import io
import shutil
import tempfile
from datetime import timedelta
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from PIL import Image

from moderation.comprehension import _solution_blocks

from . import photos
from .models import PhotoUpload, Solution, SolutionPhoto
from .services import revise_solution
from .tests import TL, ContentTestCase, make_user

MEDIA = tempfile.mkdtemp(prefix="ximaths-photos-")


def jpeg(width=400, height=300, *, exif=None, color=(240, 240, 230)):
    out = io.BytesIO()
    Image.new("RGB", (width, height), color).save(out, "JPEG", exif=exif or Image.Exif())
    return out.getvalue()


def png(width=300, height=200):
    out = io.BytesIO()
    Image.new("RGB", (width, height), "white").save(out, "PNG")
    return out.getvalue()


def phone_exif():
    """Photo prise téléphone tourné (orientation 6) avec un lieu GPS et un modèle d'appareil."""
    exif = Image.Exif()
    exif[0x0112] = 6  # Orientation : 90° dans le sens horaire
    exif[0x0110] = "Téléphone de Léa"  # Model
    exif[0x8825] = {1: "N", 2: (48.0, 51.0, 24.0)}  # GPSInfo
    return exif


@override_settings(MEDIA_ROOT=MEDIA)
class PhotoTestCase(ContentTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.student.email_verified_at = timezone.now()
        self.student.save(update_fields=["email_verified_at"])

    def open_upload(self, user=None, exercise=None):
        self.client.force_login(user or self.student)
        response = self.client.post(f"/api/exercises/{(exercise or self.exercise).pk}/photo-uploads")
        self.assertEqual(response.status_code, 201, response.content)
        self.client.logout()
        return response.json()["token"]

    def send(self, token, data=None, name="copie.jpg"):
        """Dépôt depuis le téléphone : sans session, le jeton seul."""
        return self.client.post(
            f"/api/photo-uploads/{token}/photos",
            {"photo": SimpleUploadedFile(name, data or jpeg(), content_type="image/jpeg")},
        )

    def propose(self, token=None, user=None, **extra):
        self.client.force_login(user or self.student)
        payload = {"ai_usage": "aucune", **extra}
        if token:
            payload["photo_upload"] = token
        return self.client.post(
            f"/api/exercises/{self.exercise.pk}/solutions", payload, content_type="application/json"
        )

    def stored(self, photo):
        return Path(photo.image.path)


class ProcessingTests(PhotoTestCase):
    def test_a_phone_photo_is_turned_upright_and_loses_its_metadata(self):
        data, width, height = photos.process(jpeg(400, 300, exif=phone_exif()))

        # Orientation 6 : la photo 400×300 se lit en 300×400.
        self.assertEqual((width, height), (300, 400))
        with Image.open(io.BytesIO(data)) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertEqual(image.size, (300, 400))
            self.assertEqual(len(image.getexif()), 0)
            self.assertNotIn("icc_profile", image.info)
        self.assertNotIn(b"Exif", data[:200])
        self.assertNotIn("Léa".encode(), data)

    def test_large_photos_are_reduced_to_2000_pixels(self):
        _, width, height = photos.process(jpeg(4000, 3000))
        self.assertEqual((width, height), (2000, 1500))

    def test_png_is_accepted_and_other_formats_are_not(self):
        self.assertEqual(photos.process(png())[1:], (300, 200))
        gif = io.BytesIO()
        Image.new("RGB", (10, 10)).save(gif, "GIF")
        for data in (gif.getvalue(), b"pas une image", b"\xff\xd8\xff" + b"\0" * 50):
            with self.subTest(data=data[:12]), self.assertRaises(photos.RuleError):
                photos.process(data)

    def test_heavy_photos_are_refused_before_decoding(self):
        with self.assertRaisesMessage(photos.RuleError, "10 Mo"):
            photos.process(b"\xff\xd8\xff" + b"\0" * photos.MAX_BYTES)


class UploadTests(PhotoTestCase):
    def test_the_phone_sends_photos_with_the_token_alone(self):
        token = self.open_upload()

        response = self.send(token)

        self.assertEqual(response.status_code, 201, response.content)
        state = self.client.get(f"/api/photo-uploads/{token}").json()
        self.assertEqual((state["exercise_id"], state["open"], state["max_photos"]), (self.exercise.pk, True, 3))
        self.assertEqual(len(state["photos"]), 1)
        image = self.client.get(state["photos"][0]["url"])
        self.assertEqual((image.status_code, image["Content-Type"]), (200, "image/jpeg"))
        self.assertIn("private", image["Cache-Control"])

    def test_three_photos_at_most(self):
        token = self.open_upload()
        for _ in range(3):
            self.assertEqual(self.send(token).status_code, 201)

        response = self.send(token)

        self.assertEqual(response.status_code, 409)
        self.assertIn("3 photos au plus", response.json()["detail"])

    def test_a_photo_can_be_removed_and_the_order_closes_up(self):
        token = self.open_upload()
        first, second = (self.send(token).json()["id"] for _ in range(2))
        first_path = self.stored(SolutionPhoto.objects.get(pk=first))

        self.assertEqual(self.client.delete(f"/api/photo-uploads/{token}/photos/{first}").status_code, 204)

        remaining = SolutionPhoto.objects.get()
        self.assertEqual((remaining.pk, remaining.position), (second, 0))
        self.assertFalse(first_path.exists())

    def test_the_upload_window_closes_after_30_minutes(self):
        token = self.open_upload()
        PhotoUpload.objects.filter(token=token).update(expires_at=timezone.now() - timedelta(seconds=1))

        response = self.send(token)

        self.assertEqual(response.status_code, 410)
        self.assertFalse(self.client.get(f"/api/photo-uploads/{token}").json()["open"])

    def test_its_author_can_reopen_an_expired_upload_and_keep_the_photos(self):
        token = self.open_upload()
        self.send(token)
        PhotoUpload.objects.filter(token=token).update(expires_at=timezone.now() - timedelta(seconds=1))

        self.client.force_login(make_user("intrus"))
        self.assertEqual(self.client.post(f"/api/photo-uploads/{token}/reopen").status_code, 404)
        self.client.force_login(self.student)
        state = self.client.post(f"/api/photo-uploads/{token}/reopen").json()

        self.assertTrue(state["open"])
        self.assertEqual(len(state["photos"]), 1)
        self.assertEqual(self.send(token).status_code, 201)

    def test_an_unknown_token_opens_nothing(self):
        self.assertEqual(self.send("inconnu").status_code, 404)
        self.assertEqual(self.client.get("/api/photo-uploads/inconnu").status_code, 404)

    def test_opening_an_upload_needs_a_verified_account(self):
        unverified = make_user("sans-email")
        self.client.force_login(unverified)
        self.assertEqual(self.client.post(f"/api/exercises/{self.exercise.pk}/photo-uploads").status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.post(f"/api/exercises/{self.exercise.pk}/photo-uploads").status_code, 401)

    def test_unused_photos_are_purged_after_a_day_with_their_files(self):
        token = self.open_upload()
        self.send(token)
        photo = SolutionPhoto.objects.get()
        path = self.stored(photo)
        self.assertTrue(path.exists())

        self.assertEqual(photos.purge(now=timezone.now() + timedelta(hours=23)), 0)
        self.assertEqual(photos.purge(now=timezone.now() + timedelta(days=1, minutes=1)), 1)

        self.assertFalse(SolutionPhoto.objects.exists())
        self.assertFalse(PhotoUpload.objects.exists())
        self.assertFalse(path.exists())


class SolutionWithPhotosTests(PhotoTestCase):
    def test_a_solution_can_be_photos_alone(self):
        token = self.open_upload()
        self.send(token)
        self.send(token, png(), name="page2.png")

        response = self.propose(token)

        self.assertEqual(response.status_code, 201, response.content)
        solution = Solution.objects.get(pk=response.json()["id"])
        self.assertEqual(solution.status, Solution.Status.UNDER_REVIEW)
        self.assertEqual(solution.body, "")
        self.assertEqual([p.position for p in solution.photos.all()], [0, 1])
        # Jointes : elles ne sont plus dans l'envoi, qui ne peut plus resservir.
        self.assertEqual(self.client.get(f"/api/photo-uploads/{token}").json()["photos"], [])
        self.assertIsNone(SolutionPhoto.objects.filter(solution=None).first())

    def test_a_solution_is_always_photos_never_typed_text(self):
        # Sans jeton, ou avec un envoi vide : refusé, même avec une rédaction tapée.
        self.assertEqual(self.propose(body="Une rédaction tapée, bien assez longue.").status_code, 422)
        response = self.propose(self.open_upload(), body="Une rédaction tapée, bien assez longue.")
        self.assertEqual(response.status_code, 422)
        self.assertIn("Joins les photos de ta copie", response.json()["detail"])

        token = self.open_upload()
        self.send(token)
        response = self.propose(token, body="Ignoré : une solution ne se tape plus.")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Solution.objects.get(pk=response.json()["id"]).body, "")

    def test_someone_elses_upload_cannot_be_attached(self):
        other = make_user("intrus", email_verified_at=timezone.now())
        token = self.open_upload()
        self.send(token)

        response = self.propose(token, user=other)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(Solution.objects.exists())
        self.assertEqual(SolutionPhoto.objects.filter(solution=None).count(), 1)

    def test_an_upload_for_another_exercise_cannot_be_attached(self):
        other_exercise = self.make_exercise()
        token = self.open_upload(exercise=other_exercise)
        self.send(token)
        self.assertEqual(self.propose(token).status_code, 422)

    def test_two_photo_solutions_both_go_to_review(self):
        first = make_user("marc", level="L1", email_verified_at=timezone.now())
        for author in (first, self.student):
            token = self.open_upload(user=author)
            self.send(token, jpeg(color=(200, 200, 200) if author == first else (250, 250, 250)))
            self.assertEqual(self.propose(token, user=author).status_code, 201)

        mine = Solution.objects.get(author=self.student)
        self.assertEqual(mine.status, Solution.Status.UNDER_REVIEW)

    def test_reviewers_receive_the_photos(self):
        token = self.open_upload()
        self.send(token)
        solution = Solution.objects.get(pk=self.propose(token).json()["id"])
        reviewer = solution.reviews.first().reviewer
        reviewer.email_verified_at = timezone.now()
        reviewer.save(update_fields=["email_verified_at"])

        self.client.force_login(reviewer)
        task = self.client.get("/api/reviews").json()[0]

        self.assertEqual(task["solution_body"], "")
        self.assertEqual(len(task["solution_photos"]), 1)
        self.assertEqual(self.client.get(task["solution_photos"][0]["url"]).status_code, 200)


class VisibilityTests(PhotoTestCase):
    def setUp(self):
        super().setUp()
        token = self.open_upload()
        self.send(token)
        self.solution = Solution.objects.get(pk=self.propose(token).json()["id"])
        self.url = photos.described(self.solution)[0]["url"]
        self.client.logout()

    def status_for(self, user):
        self.client.logout()
        if user is not None:
            self.client.force_login(user)
        return self.client.get(self.url).status_code

    def test_under_review_only_the_author_reviewers_and_moderators_see_them(self):
        reviewer = self.solution.reviews.first().reviewer
        self.assertEqual(self.status_for(self.student), 200)
        self.assertEqual(self.status_for(reviewer), 200)
        self.assertEqual(self.status_for(make_user("modo", trust=TL.MODERATOR)), 200)
        self.assertEqual(self.status_for(make_user("curieux")), 404)
        self.assertEqual(self.status_for(make_user("expert", trust=TL.EXPERT)), 404)
        self.assertEqual(self.status_for(None), 404)

    def test_a_validated_copy_stays_private(self):
        # Validée, la copie reste privée : son auteur et ses relecteurs seulement.
        Solution.objects.filter(pk=self.solution.pk).update(status=Solution.Status.VALIDATED)
        self.assertEqual(self.status_for(None), 404)
        self.assertEqual(self.status_for(make_user("curieux", level="L1")), 404)
        self.assertEqual(self.status_for(self.student), 200)

    def test_a_missing_file_is_not_found_rather_than_an_error(self):
        self.stored(self.solution.photos.get()).unlink()
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_the_url_must_match_its_solution(self):
        other = self.publish(author=make_user("autre", level="L1"))
        photo_id = self.solution.photos.get().pk
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(f"/api/solutions/{other.pk}/photos/{photo_id}").status_code, 404)


class RevisionWithPhotosTests(PhotoTestCase):
    def setUp(self):
        super().setUp()
        token = self.open_upload()
        self.send(token)
        self.solution = Solution.objects.get(pk=self.propose(token).json()["id"])

    def revise(self, token=None, **extra):
        self.client.force_login(self.student)
        payload = extra | ({"photo_upload": token} if token else {})
        return self.client.post(f"/api/solutions/{self.solution.pk}/revise", payload, content_type="application/json")

    def test_new_photos_replace_the_old_ones_and_go_back_to_review(self):
        Solution.objects.filter(pk=self.solution.pk).update(status=Solution.Status.VALIDATED, validated_at=timezone.now())
        old = self.solution.photos.get()
        old_path = self.stored(old)
        token = self.open_upload()
        self.send(token)
        self.send(token)

        response = self.revise(token)

        self.assertEqual(response.status_code, 200, response.content)
        self.solution.refresh_from_db()
        self.assertEqual(self.solution.status, Solution.Status.UNDER_REVIEW)
        self.assertEqual(self.solution.review_round, 2)
        self.assertEqual(self.solution.photos.count(), 2)
        self.assertFalse(SolutionPhoto.objects.filter(pk=old.pk).exists())
        self.assertFalse(old_path.exists())

    def test_a_validated_photo_solution_keeps_its_status_without_changes(self):
        Solution.objects.filter(pk=self.solution.pk).update(status=Solution.Status.VALIDATED, validated_at=timezone.now())
        self.solution.refresh_from_db()

        revised, reopened = revise_solution(self.solution, "")

        self.assertFalse(reopened)
        self.assertEqual(revised.status, Solution.Status.VALIDATED)
        self.assertEqual(revised.photos.count(), 1)

    def test_a_revision_is_new_photos(self):
        Solution.objects.filter(pk=self.solution.pk).update(status=Solution.Status.NEEDS_WORK)
        self.assertEqual(self.revise(body="J'ai complété la preuve, en détail.").status_code, 422)
        self.assertEqual(self.revise(self.open_upload()).status_code, 422)

    def test_photos_replace_an_older_typed_solution(self):
        Solution.objects.filter(pk=self.solution.pk).update(
            status=Solution.Status.NEEDS_WORK, body="Ancienne rédaction tapée, d'avant les photos."
        )
        self.solution.photos.all().delete()
        token = self.open_upload()
        self.send(token)

        self.assertEqual(self.revise(token).status_code, 200)

        self.solution.refresh_from_db()
        self.assertEqual((self.solution.body, self.solution.photos.count()), ("", 1))
        self.assertEqual(self.solution.status, Solution.Status.UNDER_REVIEW)


class ComprehensionPromptTests(PhotoTestCase):
    def test_claude_reads_the_copy_photos(self):
        token = self.open_upload()
        self.send(token)
        self.send(token)
        solution = Solution.objects.get(pk=self.propose(token).json()["id"])

        blocks = _solution_blocks(solution, "Énoncé : …\n\nSolution de l'étudiant :\n\n", "\n\nQuestion : …")

        self.assertEqual([block["type"] for block in blocks], ["text", "image", "image", "text"])
        self.assertIn("Copie manuscrite de l'étudiant, en 2 photo(s)", blocks[0]["text"])
        self.assertEqual(blocks[1]["source"]["media_type"], "image/jpeg")
        self.assertEqual(blocks[-1]["text"], "\n\nQuestion : …")

    def test_without_photos_the_prompt_stays_text(self):
        solution = self.publish()
        self.assertIsInstance(_solution_blocks(solution, "Avant : "), str)

    def test_the_data_export_lists_the_photos(self):
        from accounts.services import export_user_data

        token = self.open_upload()
        self.send(token)
        self.propose(token)

        exported = export_user_data(self.student)["solutions"][0]["photos"]

        self.assertEqual(len(exported), 1)
        self.assertTrue(exported[0].startswith("/api/solutions/"))
