import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.test.helpers import create_superuser


class FacilityDatasetThemeUploadTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facility = Facility.objects.create(name="Theme Test Facility")
        cls.superuser = create_superuser(cls.facility)
        cls.learner = FacilityUser.objects.create(
            username="test_learner",
            facility=cls.facility,
        )
        cls.learner.set_password("password")
        cls.learner.save()

    def test_upload_theme_image_as_superuser_succeeds(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("kolibri:core:facilitydataset-upload-theme-image")

        fake_image = io.BytesIO(b"dummy image data")
        uploaded_file = SimpleUploadedFile(
            "school_bg.png", fake_image.read(), content_type="image/png"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("url", response.data)
        self.assertTrue(
            response.data["url"].startswith("/media/facility_themes/backgrounds/")
        )
        self.assertEqual(response.data["file_name"], "school_bg.png")

    def test_upload_theme_image_unauthorized_user_forbidden(self):
        self.client.force_authenticate(user=self.learner)
        url = reverse("kolibri:core:facilitydataset-upload-theme-image")

        fake_image = io.BytesIO(b"dummy image data")
        uploaded_file = SimpleUploadedFile(
            "school_bg.png", fake_image.read(), content_type="image/png"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_theme_image_invalid_extension_fails(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("kolibri:core:facilitydataset-upload-theme-image")

        fake_file = io.BytesIO(b"malicious script")
        uploaded_file = SimpleUploadedFile(
            "script.exe", fake_file.read(), content_type="application/octet-stream"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
