from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.attendance.models import AttendanceRecord
from kolibri.core.attendance.models import AttendanceSession
from kolibri.core.auth.models import Classroom
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.models import Membership
from kolibri.core.auth.test.helpers import DUMMY_PASSWORD
from kolibri.core.auth.test.helpers import provision_device
from kolibri.core.coursework.models import Assignment
from kolibri.core.coursework.models import AssignmentSubmission


class AtRiskAnalyticsAPITestCase(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        provision_device()
        cls.facility = Facility.objects.create(name="EWS Test Facility")
        cls.classroom = Classroom.objects.create(
            name="Grade 10 - Rizal", parent=cls.facility
        )

        cls.coach = FacilityUser.objects.create(
            username="teacher_maria", facility=cls.facility
        )
        cls.coach.set_password(DUMMY_PASSWORD)
        cls.coach.save()
        cls.classroom.add_coach(cls.coach)

        cls.learner1 = FacilityUser.objects.create(
            username="student_at_risk",
            full_name="Juan Dela Cruz",
            facility=cls.facility,
        )
        cls.learner1.set_password(DUMMY_PASSWORD)
        cls.learner1.save()
        Membership.objects.create(user=cls.learner1, collection=cls.classroom)

        cls.learner2 = FacilityUser.objects.create(
            username="student_on_track", full_name="Maria Clara", facility=cls.facility
        )
        cls.learner2.set_password(DUMMY_PASSWORD)
        cls.learner2.save()
        Membership.objects.create(user=cls.learner2, collection=cls.classroom)

        # Setup attendance sessions (2 sessions)
        s1 = AttendanceSession.objects.create(
            collection=cls.classroom, created_by=cls.coach
        )
        s2 = AttendanceSession.objects.create(
            collection=cls.classroom, created_by=cls.coach
        )

        # Learner 1 attended 0 of 2 sessions (0% attendance -> <80% risk trigger)
        AttendanceRecord.objects.create(
            attendance_session=s1, user=cls.learner1, present=False
        )
        AttendanceRecord.objects.create(
            attendance_session=s2, user=cls.learner1, present=False
        )

        # Learner 2 attended both sessions (100% attendance)
        AttendanceRecord.objects.create(
            attendance_session=s1, user=cls.learner2, present=True
        )
        AttendanceRecord.objects.create(
            attendance_session=s2, user=cls.learner2, present=True
        )

        # Setup 2 assignments
        a1 = Assignment.objects.create(
            title="Homework 1", collection=cls.classroom, created_by=cls.coach
        )
        a2 = Assignment.objects.create(
            title="Homework 2", collection=cls.classroom, created_by=cls.coach
        )

        # Learner 2 submitted both
        AssignmentSubmission.objects.create(
            assignment=a1, learner=cls.learner2, text_content="Answer 1"
        )
        AssignmentSubmission.objects.create(
            assignment=a2, learner=cls.learner2, text_content="Answer 2"
        )

        # Learner 1 submitted none (2 missing -> missing_work trigger)

    def _login(self, user):
        self.client.login(
            username=user.username, password=DUMMY_PASSWORD, facility=self.facility
        )

    def test_at_risk_analytics_identifies_risk_factors(self):
        self._login(self.coach)
        url = reverse("kolibri:core:atriskanalytics-list")
        response = self.client.get(url, {"collection": self.classroom.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["total_learners"], 2)
        self.assertEqual(data["high_risk_count"], 1)
        self.assertEqual(data["on_track_count"], 1)

        # Find Juan Dela Cruz (at-risk)
        at_risk = next(
            l for l in data["learners"] if l["username"] == "student_at_risk"
        )
        self.assertEqual(at_risk["risk_level"], "high")
        # Should have attendance risk factor and missing_work risk factor
        categories = [f["category"] for f in at_risk["risk_factors"]]
        self.assertIn("attendance", categories)
        self.assertIn("missing_work", categories)

        # Find Maria Clara (on track)
        on_track = next(
            l for l in data["learners"] if l["username"] == "student_on_track"
        )
        self.assertEqual(on_track["risk_level"], "low")
        self.assertEqual(len(on_track["risk_factors"]), 0)

    def test_coach_can_log_and_update_learner_intervention(self):
        self._login(self.coach)
        url = reverse("kolibri:core:learnerintervention-list")
        payload = {
            "collection": self.classroom.id,
            "learner": self.learner1.id,
            "risk_level": "high",
            "reasons": ["low_attendance", "missing_homework"],
            "intervention_type": "remedial_instruction",
            "notes": "Scheduled 1-on-1 remedial review on Friday.",
            "status": "in_progress",
        }
        create_res = self.client.post(url, payload, format="json")
        self.assertEqual(
            create_res.status_code, status.HTTP_201_CREATED, create_res.data
        )
        itv_id = create_res.data["id"]

        # Update status to resolved
        detail_url = reverse(
            "kolibri:core:learnerintervention-detail", kwargs={"pk": itv_id}
        )
        update_res = self.client.patch(
            detail_url,
            {"status": "resolved", "notes": "Completed and caught up."},
            format="json",
        )
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        self.assertEqual(update_res.data["status"], "resolved")

        # Verify it reflects in AtRiskAnalytics
        analytics_url = reverse("kolibri:core:atriskanalytics-list")
        analytics_res = self.client.get(
            analytics_url, {"collection": self.classroom.id}
        )
        at_risk = next(
            l
            for l in analytics_res.data["learners"]
            if l["username"] == "student_at_risk"
        )
        self.assertEqual(len(at_risk["interventions"]), 1)
        self.assertEqual(at_risk["interventions"][0]["status"], "resolved")
