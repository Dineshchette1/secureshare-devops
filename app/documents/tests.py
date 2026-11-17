"""Tests for SecureShare.

These run in CI on every push. They cover the behaviour that matters:
health probes, upload validation, and the share-link security rules.
"""

import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Document

# Write uploaded test files to a throwaway directory, never app/media/.
TEMP_MEDIA = tempfile.mkdtemp(prefix="secureshare-tests-")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class SecureShareTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    @staticmethod
    def a_pdf(name="report.pdf", size=1024):
        return SimpleUploadedFile(name, b"x" * size, content_type="application/pdf")


class HealthEndpointTests(SecureShareTestCase):
    def test_healthz_reports_ok(self):
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_readyz_reports_database_up(self):
        response = self.client.get(reverse("readyz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["database"], "up")


class UploadTests(SecureShareTestCase):
    def test_upload_creates_document_with_metadata(self):
        response = self.client.post(
            reverse("document_list"),
            {"title": "Quarterly report", "file": self.a_pdf(size=2048)},
        )
        self.assertEqual(response.status_code, 302)  # redirect after success

        document = Document.objects.get()
        self.assertEqual(document.title, "Quarterly report")
        self.assertEqual(document.original_name, "report.pdf")
        self.assertEqual(document.size_bytes, 2048)
        self.assertFalse(document.is_expired)

    def test_each_upload_gets_a_unique_share_token(self):
        for i in range(2):
            self.client.post(
                reverse("document_list"),
                {"title": f"Doc {i}", "file": self.a_pdf(name=f"doc{i}.pdf")},
            )
        tokens = {doc.share_token for doc in Document.objects.all()}
        self.assertEqual(len(tokens), 2)

    def test_upload_rejects_disallowed_extension(self):
        bad_file = SimpleUploadedFile("malware.exe", b"MZ", content_type="application/x-msdownload")
        response = self.client.post(
            reverse("document_list"), {"title": "Bad", "file": bad_file}
        )

        self.assertEqual(response.status_code, 200)  # form redisplayed
        self.assertContains(response, "not allowed")
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_rejects_oversized_file(self):
        big_file = self.a_pdf(size=11 * 1024 * 1024)  # 11 MB, limit is 10
        response = self.client.post(
            reverse("document_list"), {"title": "Huge", "file": big_file}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "too large")
        self.assertEqual(Document.objects.count(), 0)


class ShareLinkTests(SecureShareTestCase):
    def setUp(self):
        self.document = Document.objects.create(
            title="Shared report",
            file=self.a_pdf(),
            original_name="report.pdf",
            size_bytes=1024,
        )

    def test_valid_share_link_downloads_the_file(self):
        response = self.client.get(
            reverse("share_download", args=[self.document.share_token])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("report.pdf", response["Content-Disposition"])

    def test_download_increments_the_counter(self):
        url = reverse("share_download", args=[self.document.share_token])
        self.client.get(url).close()
        self.client.get(url).close()

        self.document.refresh_from_db()
        self.assertEqual(self.document.download_count, 2)

    def test_expired_share_link_is_rejected(self):
        self.document.expires_at = timezone.now() - timedelta(seconds=1)
        self.document.save()

        response = self.client.get(
            reverse("share_download", args=[self.document.share_token])
        )
        self.assertEqual(response.status_code, 404)

    def test_unknown_token_is_rejected(self):
        response = self.client.get(
            "/s/00000000-0000-4000-8000-000000000000/"
        )
        self.assertEqual(response.status_code, 404)

    def test_malformed_token_is_rejected(self):
        response = self.client.get("/s/not-a-uuid/")
        self.assertEqual(response.status_code, 404)
