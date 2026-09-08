from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.auth.test.helpers import create_superuser
from kolibri.core.auth.test.helpers import provision_device
from kolibri.core.auth.test.test_api import FacilityFactory


class LiveClassSessionApiTestCase(APITestCase):
    databases = "__all__"

    def setUp(self):
        super(LiveClassSessionApiTestCase, self).setUp()
        self.facility = FacilityFactory.create()
        provision_device()
        self.admin = create_superuser(self.facility)
        self.client.login(username=self.admin.username, password="password")
        self.url = reverse("kolibri:kolibri.core.device:live_sessions")

    def test_post_with_room_name_only(self):
        response = self.client.post(
            self.url,
            {"room_name": "room_ehy6o5", "active": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["room_name"], "room_ehy6o5")

        get_res = self.client.get(self.url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertIn("room_ehy6o5", get_res.data)
        self.assertTrue(get_res.data["room_ehy6o5"]["active"])

    def test_post_with_class_id_and_room_name(self):
        response = self.client.post(
            self.url,
            {
                "class_id": "class-12345",
                "room_name": "phiedu_class_class-12345",
                "active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_res = self.client.get(self.url)
        self.assertIn("class-12345", get_res.data)
        self.assertTrue(get_res.data["class-12345"]["active"])

    def test_deactivate_room(self):
        self.client.post(
            self.url,
            {"room_name": "room_to_close", "active": True},
            format="json",
        )
        get_res = self.client.get(self.url)
        self.assertIn("room_to_close", get_res.data)

        self.client.post(
            self.url,
            {"room_name": "room_to_close", "active": False},
            format="json",
        )
        get_res2 = self.client.get(self.url)
        self.assertNotIn("room_to_close", get_res2.data)

    def test_missing_both_class_id_and_room_name_fails(self):
        response = self.client.post(
            self.url,
            {"active": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
