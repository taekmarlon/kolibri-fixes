import io
import zipfile
from unittest.mock import patch

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


class LessonCustomResourcesTestCase(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        provision_device()
        cls.facility = Facility.objects.create(name="CustomResourceFacility")
        cls.admin = FacilityUser.objects.create(
            username="admin_coach", facility=cls.facility
        )
        cls.admin.set_password(DUMMY_PASSWORD)
        cls.admin.save()
        cls.facility.add_admin(cls.admin)

        cls.learner = FacilityUser.objects.create(
            username="learner_user", facility=cls.facility
        )
        cls.learner.set_password(DUMMY_PASSWORD)
        cls.learner.save()

        cls.classroom = Classroom.objects.create(
            name="Classroom 1", parent=cls.facility
        )
        cls.classroom.add_member(cls.learner)

        cls.lesson = Lesson.objects.create(
            title="Interactive Lesson",
            description="A lesson with custom resources",
            is_active=True,
            collection=cls.classroom,
            created_by=cls.admin,
        )

    def test_add_youtube_custom_resource(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        payload = {
            "resource_type": "youtube",
            "title": "Introduction to Fractions",
            "description": "Watch this introductory video on fractions.",
            "url": "https://www.youtube.com/watch?v=0k2ZzkwW444",
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data.get("is_custom"))
        self.assertEqual(data.get("resource_type"), "youtube")
        self.assertEqual(data.get("title"), "Introduction to Fractions")
        self.assertIn("0k2ZzkwW444", data.get("url"))

        # Verify saved in lesson
        self.lesson.refresh_from_db()
        self.assertEqual(len(self.lesson.resources), 1)
        self.assertEqual(self.lesson.resources[0]["resource_type"], "youtube")
        self.assertTrue(self.lesson.resources[0]["is_custom"])

    def test_upload_pdf_custom_resource(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        dummy_pdf = SimpleUploadedFile(
            "worksheet.pdf",
            b"%PDF-1.4 dummy pdf content",
            content_type="application/pdf",
        )
        payload = {
            "title": "Fractions Worksheet",
            "description": "Practice worksheet",
            "file": dummy_pdf,
        }
        response = self.client.post(url, data=payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data.get("is_custom"))
        self.assertEqual(data.get("resource_type"), "pdf")
        self.assertEqual(data.get("file_name"), "worksheet.pdf")
        self.assertTrue(data.get("file_url").startswith("/media/"))

        self.lesson.refresh_from_db()
        self.assertEqual(len(self.lesson.resources), 1)
        self.assertEqual(self.lesson.resources[0]["resource_type"], "pdf")

    def test_upload_file_exceeding_5mb_fails(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        oversized_pdf = SimpleUploadedFile(
            "large_worksheet.pdf",
            b"x" * (5 * 1024 * 1024 + 100),
            content_type="application/pdf",
        )
        payload = {
            "title": "Large Fractions Worksheet",
            "description": "Too big worksheet",
            "file": oversized_pdf,
        }
        response = self.client.post(url, data=payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("exceeds the 5MB maximum limit", response.data.get("detail", ""))

    def test_upload_html5_zip_custom_resource(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )

        # Create a simple zip archive containing index.html
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "index.html", "<html><body><h1>Simulation</h1></body></html>"
            )
        zip_buffer.seek(0)
        uploaded_zip = SimpleUploadedFile(
            "simulation.zip", zip_buffer.read(), content_type="application/zip"
        )

        payload = {
            "title": "Math Simulation",
            "description": "Interactive HTML5 game",
            "file": uploaded_zip,
        }
        response = self.client.post(url, data=payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data.get("is_custom"))
        self.assertEqual(data.get("resource_type"), "html5")
        self.assertTrue(data.get("file_url").endswith("index.html"))

    def test_add_ai_text_custom_resource(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        payload = {
            "resource_type": "ai_text",
            "title": "AI Study Notes: Fractions",
            "description": "Comprehensive explanation generated by AI",
            "content": "# Fractions\n\nA fraction represents a part of a whole.",
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data.get("is_custom"))
        self.assertEqual(data.get("resource_type"), "ai_text")
        self.assertIn("Fractions", data.get("content"))

    def test_upload_h5p_file_custom_resource(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )

        # Create a mock .h5p archive containing h5p.json and content/
        h5p_buffer = io.BytesIO()
        with zipfile.ZipFile(h5p_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "h5p.json",
                '{"title": "Test Interactive", "mainLibrary": "H5P.MultiChoice"}',
            )
            zip_file.writestr("content/content.json", '{"question": "What is 2+2?"}')
            zip_file.writestr(
                "index.html",
                "<!DOCTYPE html><html><body>Interactive H5P Content</body></html>",
            )
        h5p_buffer.seek(0)
        uploaded_h5p = SimpleUploadedFile(
            "interactive_activity.h5p",
            h5p_buffer.read(),
            content_type="application/zip",
        )

        payload = {
            "title": "Interactive Exercise",
            "description": "H5P interactive package",
            "file": uploaded_h5p,
            "resource_type": "h5p",
        }
        response = self.client.post(url, data=payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data.get("is_custom"))
        self.assertEqual(data.get("resource_type"), "h5p")
        self.assertTrue(data.get("file_url").endswith("index.html"))

        self.lesson.refresh_from_db()
        self.assertEqual(len(self.lesson.resources), 1)
        self.assertEqual(self.lesson.resources[0]["resource_type"], "h5p")

    def test_add_compiled_interactive_custom_resource(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        html_code = (
            "<!DOCTYPE html><html><head><title>Quiz</title></head>"
            "<body><div id='app'>Interactive Quiz App</div></body></html>"
        )
        payload = {
            "resource_type": "h5p",
            "title": "Interactive Biology Quiz",
            "description": "Multiple choice quiz created in-system",
            "content": html_code,
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data.get("is_custom"))
        self.assertEqual(data.get("resource_type"), "h5p")
        self.assertEqual(data.get("title"), "Interactive Biology Quiz")
        self.assertTrue(data.get("file_url").endswith("index.html"))

        self.lesson.refresh_from_db()
        self.assertEqual(len(self.lesson.resources), 1)
        self.assertEqual(self.lesson.resources[0]["resource_type"], "h5p")

    def test_learner_cannot_add_custom_resource(self):
        self.client.login(username=self.learner.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        payload = {
            "resource_type": "youtube",
            "title": "Learner Video",
            "url": "https://www.youtube.com/watch?v=0k2ZzkwW444",
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_size_action_with_custom_resources(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        # Add a custom resource to lesson
        self.lesson.resources = [
            {
                "contentnode_id": "11111111111111111111111111111111",
                "content_id": "11111111111111111111111111111111",
                "channel_id": "00000000000000000000000000000000",
                "is_custom": True,
                "resource_type": "pdf",
                "title": "Custom Doc",
                "file_size": 2048,
            }
        ]
        self.lesson.save()

        url = reverse("kolibri:core:lesson-size")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not crash and should return a dict containing the lesson
        lessons_sizes = response.data
        lesson_size = next(
            (item[self.lesson.id] for item in lessons_sizes if self.lesson.id in item),
            None,
        )
        self.assertIsNotNone(lesson_size)
        self.assertEqual(lesson_size, 2048)

    def test_learner_lesson_consolidation_with_custom_resource(self):
        # Assign lesson to classroom
        from kolibri.core.lessons.models import LessonAssignment

        LessonAssignment.objects.get_or_create(
            lesson=self.lesson, collection=self.classroom, assigned_by=self.admin
        )
        self.lesson.resources = [
            {
                "contentnode_id": "22222222222222222222222222222222",
                "content_id": "22222222222222222222222222222222",
                "channel_id": "00000000000000000000000000000000",
                "is_custom": True,
                "resource_type": "youtube",
                "title": "Custom YouTube Lesson",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            }
        ]
        self.lesson.save()

        self.client.login(username=self.learner.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:kolibri.plugins.learn:learnerlesson-detail",
            kwargs={"pk": self.lesson.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson_data = response.data
        self.assertEqual(len(lesson_data["resources"]), 1)
        self.assertFalse(lesson_data["missing_resource"])
        resource = lesson_data["resources"][0]
        self.assertTrue(resource["is_custom"])
        self.assertIsNotNone(resource.get("contentnode"))
        self.assertEqual(resource["contentnode"]["kind"], "video")

    def test_add_h5p_with_bundle_fetch(self):
        self.client.login(username=self.admin.username, password=DUMMY_PASSWORD)
        url = reverse(
            "kolibri:core:lesson-custom-resource", kwargs={"pk": self.lesson.id}
        )
        mock_html = "<html><body><div class='h5p-content'>H5P Interactive Test</div></body></html>"
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = mock_html
            payload = {
                "resource_type": "h5p",
                "h5p_content_id": "test_12345",
                "title": "Interactive Video Activity",
                "description": "Watch and interact with the video.",
            }
            response = self.client.post(url, data=payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["resource_type"], "h5p")
            self.assertEqual(response.data["title"], "Interactive Video Activity")
            self.assertEqual(response.data["h5p_content_id"], "test_12345")
            self.assertTrue(response.data["file_url"].endswith("/index.html"))

    def test_h5p_proxy_view(self):
        mock_html = "<html><body><form id='h5p-content-form'></form></body></html>"
        with patch("requests.request") as mock_req:
            mock_req.return_value.status_code = 200
            mock_req.return_value.headers = {"content-type": "text/html; charset=utf-8"}
            mock_req.return_value.content = mock_html.encode("utf-8")
            mock_req.return_value.text = mock_html
            url = reverse("kolibri:core:h5p_proxy", kwargs={"path": "new"})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("KOLIBRI_H5P_SAVED", response.content.decode("utf-8"))
