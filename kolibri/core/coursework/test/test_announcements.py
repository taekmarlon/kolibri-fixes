"""
Priority 6 — School Events & Announcements Board
TDD Test Suite using Kolibri's standard APITestCase pattern.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.auth.models import Classroom
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.models import Membership
from kolibri.core.auth.test.helpers import DUMMY_PASSWORD
from kolibri.core.auth.test.helpers import provision_device
from kolibri.core.coursework.models import Announcement

ANNOUNCEMENT_LIST_URL = "/api/coursework/announcement/"


def announcement_detail_url(pk):
    return f"/api/coursework/announcement/{pk}/"


class AnnouncementCoachTestCase(APITestCase):
    """Tests for coach creating and managing class-level announcements."""

    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        provision_device()
        cls.facility = Facility.objects.create(name="Cedarhall Test Facility")
        cls.classroom = Classroom.objects.create(
            name="Grade 5 - Einstein", parent=cls.facility
        )

        cls.coach = FacilityUser.objects.create(
            username="coach_ann_p6", full_name="Coach Reyes", facility=cls.facility
        )
        cls.coach.set_password(DUMMY_PASSWORD)
        cls.coach.save()
        cls.classroom.add_coach(cls.coach)

        cls.learner = FacilityUser.objects.create(
            username="learner_ann_p6", full_name="Maria Reyes", facility=cls.facility
        )
        cls.learner.set_password(DUMMY_PASSWORD)
        cls.learner.save()
        Membership.objects.create(user=cls.learner, collection=cls.classroom)

    def test_coach_can_create_class_announcement(self):
        """Coach creates a class-level announcement; it appears in list."""
        self.client.login(username="coach_ann_p6", password=DUMMY_PASSWORD)
        resp = self.client.post(
            ANNOUNCEMENT_LIST_URL,
            {
                "title": "Science Project Due Friday",
                "body": "Submit your poster by Friday 4 PM.",
                "announcement_type": "general",
                "scope": "class",
                "collection": self.classroom.id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data["title"], "Science Project Due Friday")
        self.assertEqual(resp.data["scope"], "class")

    def test_learner_can_read_class_announcement(self):
        """Learner in the class can read announcements posted for that class."""
        # Create announcement as coach
        self.client.login(username="coach_ann_p6", password=DUMMY_PASSWORD)
        create_resp = self.client.post(
            ANNOUNCEMENT_LIST_URL,
            {
                "title": "Parent-Teacher Meeting",
                "body": "This Friday at 2 PM in Room 101.",
                "announcement_type": "event",
                "scope": "class",
                "collection": self.classroom.id,
            },
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        ann_id = create_resp.data["id"]

        # Read as learner
        self.client.login(username="learner_ann_p6", password=DUMMY_PASSWORD)
        list_resp = self.client.get(
            f"{ANNOUNCEMENT_LIST_URL}?collection={self.classroom.id}"
        )
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        ids = [a["id"] for a in list_resp.data]
        self.assertIn(ann_id, ids)

    def test_expired_announcement_excluded(self):
        """Announcements with past expiry_date should NOT appear in list."""
        import datetime as dt_module

        from django.utils import timezone as tz

        # Create an expired announcement directly via ORM — bypasses device provisioning check
        Announcement.objects.create(
            title="Old Expired Notice",
            body="This is outdated.",
            announcement_type="general",
            scope="class",
            collection=self.classroom,
            created_by=self.coach,
            is_active=True,
            expiry_date=tz.now() - dt_module.timedelta(days=30),
        )

        self.client.login(username="coach_ann_p6", password=DUMMY_PASSWORD)
        list_resp = self.client.get(
            f"{ANNOUNCEMENT_LIST_URL}?collection={self.classroom.id}"
        )
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        titles = [a["title"] for a in list_resp.data]
        self.assertNotIn("Old Expired Notice", titles)

    def test_coach_can_delete_own_announcement(self):
        """Coach can delete their own announcement."""
        self.client.login(username="coach_ann_p6", password=DUMMY_PASSWORD)
        create_resp = self.client.post(
            ANNOUNCEMENT_LIST_URL,
            {
                "title": "Temporary Notice",
                "body": "Will be deleted.",
                "announcement_type": "general",
                "scope": "class",
                "collection": self.classroom.id,
            },
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        ann_id = create_resp.data["id"]

        del_resp = self.client.delete(announcement_detail_url(ann_id))
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)

        list_resp = self.client.get(
            f"{ANNOUNCEMENT_LIST_URL}?collection={self.classroom.id}"
        )
        ids = [a["id"] for a in list_resp.data]
        self.assertNotIn(ann_id, ids)


class AnnouncementAdminTestCase(APITestCase):
    """Tests for admin creating facility-wide announcements."""

    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        provision_device()
        cls.facility = Facility.objects.create(name="Cedarhall Admin Facility")
        cls.classroom = Classroom.objects.create(
            name="Grade 1 - Diamond", parent=cls.facility
        )

        cls.admin = FacilityUser.objects.create(
            username="admin_ann_p6", full_name="Principal Cruz", facility=cls.facility
        )
        cls.admin.set_password(DUMMY_PASSWORD)
        cls.admin.save()
        cls.facility.add_admin(cls.admin)

    def test_admin_can_create_facility_announcement(self):
        """Admin can create a facility-wide announcement."""
        self.client.login(username="admin_ann_p6", password=DUMMY_PASSWORD)
        resp = self.client.post(
            ANNOUNCEMENT_LIST_URL,
            {
                "title": "Foundation Day — Classes Suspended",
                "body": "No classes on September 15 in observance of Foundation Day.",
                "announcement_type": "event",
                "scope": "facility",
                "collection": self.facility.id,
                "event_date": "2026-09-15T08:00:00Z",
                "is_pinned": True,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data["scope"], "facility")
        self.assertEqual(resp.data["announcement_type"], "event")
        self.assertTrue(resp.data["is_pinned"])

    def test_pinned_announcements_appear_first(self):
        """Pinned announcements are ordered before non-pinned ones."""
        self.client.login(username="admin_ann_p6", password=DUMMY_PASSWORD)

        self.client.post(
            ANNOUNCEMENT_LIST_URL,
            {
                "title": "Regular Circular",
                "body": "Routine info.",
                "announcement_type": "general",
                "scope": "facility",
                "collection": self.facility.id,
                "is_pinned": False,
            },
            format="json",
        )
        self.client.post(
            ANNOUNCEMENT_LIST_URL,
            {
                "title": "PINNED: Emergency Notice",
                "body": "Critical school update.",
                "announcement_type": "urgent",
                "scope": "facility",
                "collection": self.facility.id,
                "is_pinned": True,
            },
            format="json",
        )

        list_resp = self.client.get(
            f"{ANNOUNCEMENT_LIST_URL}?collection={self.facility.id}"
        )
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        titles = [a["title"] for a in list_resp.data]
        self.assertLess(
            titles.index("PINNED: Emergency Notice"),
            titles.index("Regular Circular"),
            "Pinned announcement should appear before non-pinned",
        )
