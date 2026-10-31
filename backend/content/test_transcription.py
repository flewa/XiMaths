import json
from unittest import mock

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from config import llm
from duplicates.test_llm import response

from . import transcription
from .tests import ContentTestCase

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 64


def claude(answer):
    client = mock.Mock()
    client.with_options.return_value = client
    client.beta.messages.create.return_value = response(json.dumps(answer))
    return client


@override_settings(ANTHROPIC_API_KEY="test")
class TranscriptionTests(ContentTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.client.force_login(self.student)
        self.student.email_verified_at = self.student.date_joined
        self.student.save()

    def upload(self, data=JPEG, *, name="copie.jpg", exercise=None):
        url = f"/api/exercises/{(exercise or self.exercise).pk}/transcription"
        return self.client.post(url, {"photo": SimpleUploadedFile(name, data, content_type="image/jpeg")})

    def test_the_photo_comes_back_as_markdown_and_latex(self):
        client = claude({"legible": True, "text": "On compare avec $\\frac{1}{n(n-1)}$.\n"})
        with mock.patch.object(llm, "_client", return_value=client):
            result = self.upload()

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"text": "On compare avec $\\frac{1}{n(n-1)}$."})
        request = client.beta.messages.create.call_args.kwargs
        self.assertEqual(request["model"], llm.TRANSCRIPTION_MODEL)
        image, text = request["messages"][0]["content"]
        self.assertEqual(image["source"]["media_type"], "image/jpeg")
        self.assertIn(self.exercise.statement, text["text"])
        self.assertIn("ne corrige rien", request["system"])
        # Pendant la requête : un délai court et sans nouvel essai, sous celui de gunicorn.
        client.with_options.assert_called_once_with(timeout=transcription.TIMEOUT, max_retries=0)

    def test_formats_are_recognised_by_their_bytes(self):
        self.assertEqual(transcription.media_type(JPEG), "image/jpeg")
        self.assertEqual(transcription.media_type(PNG), "image/png")
        self.assertEqual(transcription.media_type(WEBP), "image/webp")
        self.assertIsNone(transcription.media_type(b"GIF89a"))

        with mock.patch.object(llm, "_client") as client:
            result = self.upload(b"%PDF-1.7", name="copie.jpg")
        self.assertEqual(result.status_code, 422)
        client.assert_not_called()

    def test_heavy_photos_are_refused(self):
        with mock.patch.object(llm, "_client") as client:
            result = self.upload(JPEG + b"\x00" * transcription.MAX_BYTES)
        self.assertEqual(result.status_code, 413)
        client.assert_not_called()

    def test_an_illegible_photo_says_so(self):
        with mock.patch.object(llm, "_client", return_value=claude({"legible": False, "text": ""})):
            result = self.upload()
        self.assertEqual(result.status_code, 422)
        self.assertIn("lisible", result.json()["detail"])

    @override_settings(ANTHROPIC_API_KEY="")
    def test_without_llm_the_service_is_unavailable(self):
        self.assertEqual(self.client.get("/api/transcription").json(), {"available": False})
        self.assertEqual(self.upload().status_code, 503)

    def test_only_contributors_on_published_exercises(self):
        self.assertEqual(self.client.get("/api/transcription").json(), {"available": True})
        self.student.email_verified_at = None
        self.student.save()
        self.assertEqual(self.upload().status_code, 403)
        self.client.logout()
        self.assertEqual(self.upload().status_code, 401)

    def test_ten_photos_an_hour(self):
        with mock.patch.object(llm, "_client", return_value=claude({"legible": True, "text": "Preuve."})):
            statuses = [self.upload().status_code for _ in range(11)]
        self.assertEqual(statuses[:10], [200] * 10)
        self.assertEqual(statuses[10], 429)
