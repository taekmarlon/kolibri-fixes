from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.device.models import DeviceSettings
from kolibri.core.device.models import extra_settings_default_values


class AiApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facility = Facility.objects.create(name="Test Facility")
        cls.superuser = FacilityUser.objects.create_superuser(
            "admin", "password", cls.facility
        )
        cls.learner = FacilityUser.objects.create(
            username="student", facility=cls.facility
        )
        extra = dict(extra_settings_default_values)
        extra.update(
            {
                "ai_tutor_enabled": True,
                "ai_provider": "gemini",
                "ai_api_key": "test_key",
                "ai_model_name": "gemini-1.5-flash",
            }
        )
        cls.device_settings = DeviceSettings.objects.create(
            is_provisioned=True,
            extra_settings=extra,
        )

    def test_ai_status_endpoint(self):
        url = reverse("kolibri:core:ai_status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["enabled"])
        self.assertEqual(response.data["provider"], "gemini")
        self.assertEqual(response.data["model_name"], "gemini-1.5-flash")
        self.assertTrue(response.data["has_api_key"])

    @patch("kolibri.core.ai.viewsets.call_ai_chat")
    def test_ai_chat_endpoint_authenticated(self, mock_call_ai_chat):
        mock_call_ai_chat.return_value = (
            "Here is a step-by-step explanation of quadratic equations."
        )
        self.client.force_authenticate(user=self.learner)
        url = reverse("kolibri:core:ai_chat")
        response = self.client.post(
            url,
            {
                "messages": [
                    {"role": "user", "content": "How do I solve quadratic equations?"}
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["reply"],
            "Here is a step-by-step explanation of quadratic equations.",
        )

    @patch("kolibri.core.ai.viewsets.call_ai_chat")
    def test_ai_generate_quiz_endpoint(self, mock_call_ai_chat):
        mock_call_ai_chat.return_value = (
            "1. What is 2 + 2?\nA) 3\nB) 4\nC) 5\nAnswer: B"
        )
        self.client.force_authenticate(user=self.superuser)
        url = reverse("kolibri:core:ai_generate_quiz")
        response = self.client.post(
            url,
            {
                "topic": "Addition",
                "grade_level": "Elementary School",
                "num_questions": 3,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("What is 2 + 2?", response.data["quiz"])

    @patch("kolibri.core.ai.viewsets.call_ai_chat")
    def test_ai_generate_lesson_endpoint(self, mock_call_ai_chat):
        mock_call_ai_chat.return_value = (
            "### Lesson Plan: Newton's Laws\n1. Objectives..."
        )
        self.client.force_authenticate(user=self.superuser)
        url = reverse("kolibri:core:ai_generate_lesson")
        response = self.client.post(
            url,
            {
                "topic": "Newton's Laws",
                "grade_level": "Middle School",
                "duration": "45 minutes",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Lesson Plan", response.data["lesson"])
