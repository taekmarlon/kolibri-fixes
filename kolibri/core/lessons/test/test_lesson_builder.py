import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from kolibri.core.auth.models import Classroom
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.test.helpers import KolibriAPITestCase as APITestCase
from kolibri.core.auth.test.helpers import provision_device
from kolibri.core.lessons.models import Lesson

DUMMY_PASSWORD = "password"


class LessonBuilderTestCase(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        provision_device()
        cls.facility = Facility.objects.create(name="BuilderFacility")
        cls.admin = FacilityUser.objects.create(
            username="builder_coach", facility=cls.facility
        )
        cls.admin.set_password(DUMMY_PASSWORD)
        cls.admin.save()
        cls.facility.add_admin(cls.admin)

        cls.classroom = Classroom.objects.create(
            name="Science Class", parent=cls.facility
        )

        cls.lesson = Lesson.objects.create(
            title="Biology Unit 1",
            description="Cell Structure and Functions",
            is_active=True,
            collection=cls.classroom,
            created_by=cls.admin,
        )

    def test_add_lesson_builder_custom_resource(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        blocks = [
            {
                "id": "block-1",
                "type": "heading",
                "title": "Introduction to Plant Cells",
                "subtitle": "Discover the building blocks of flora",
            },
            {
                "id": "block-2",
                "type": "text",
                "text": "Plant cells are eukaryotic cells with chloroplasts and cell walls.",
            },
            {
                "id": "block-3",
                "type": "callout",
                "callout_type": "concept",
                "title": "Core Definition",
                "text": "Chloroplasts conduct photosynthesis.",
            },
            {
                "id": "block-4",
                "type": "checkpoint",
                "question": "What pigment gives plants their green color?",
                "answer": "Chlorophyll",
            },
        ]
        payload = {
            "resource_type": "lesson_builder",
            "title": "Interactive Plant Cells Study Module",
            "description": "Comprehensive guide to cellular biology",
            "content": json.dumps(blocks),
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data.get("is_custom"))
        self.assertEqual(data.get("resource_type"), "lesson_builder")
        self.assertEqual(data.get("title"), "Interactive Plant Cells Study Module")
        self.assertIn("Chloroplasts conduct photosynthesis", data.get("content"))

        # Verify saved in lesson model
        self.lesson.refresh_from_db()
        self.assertEqual(len(self.lesson.resources), 1)
        res = self.lesson.resources[0]
        self.assertEqual(res["resource_type"], "lesson_builder")
        self.assertTrue(res["is_custom"])
        parsed_blocks = json.loads(res["content"])
        self.assertEqual(len(parsed_blocks), 4)
        self.assertEqual(parsed_blocks[0]["type"], "heading")

    def test_upload_image_endpoint(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse("kolibri:core:lesson-upload-image")
        fake_image = SimpleUploadedFile(
            "diagram.png", b"\x89PNG\r\n\x1a\nfakecontent", content_type="image/png"
        )
        response = self.client.post(url, data={"file": fake_image}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("url", response.data)
        self.assertTrue(response.data["url"].startswith("/media/lessons/images/"))
        self.assertTrue(response.data["url"].endswith("diagram.png"))

    def test_upload_image_exceeds_5mb(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse("kolibri:core:lesson-upload-image")
        large_content = b"0" * (5 * 1024 * 1024 + 10)
        large_image = SimpleUploadedFile(
            "large_diagram.png", large_content, content_type="image/png"
        )
        response = self.client.post(url, data={"file": large_image}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("5MB maximum limit", response.data.get("detail", ""))

    def test_upload_image_unsupported_extension(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse("kolibri:core:lesson-upload-image")
        invalid_file = SimpleUploadedFile(
            "script.exe", b"binarydata", content_type="application/octet-stream"
        )
        response = self.client.post(
            url, data={"file": invalid_file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Unsupported image file extension", response.data.get("detail", "")
        )

    def test_upload_image_unauthenticated(self):
        url = reverse("kolibri:core:lesson-upload-image")
        fake_image = SimpleUploadedFile(
            "diagram.png", b"image", content_type="image/png"
        )
        response = self.client.post(url, data={"file": fake_image}, format="multipart")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
