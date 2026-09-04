from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.auth.models import Classroom
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.models import Membership
from kolibri.core.auth.test.helpers import DUMMY_PASSWORD
from kolibri.core.auth.test.helpers import provision_device
from kolibri.core.coursework.models import Assignment
from kolibri.core.coursework.models import AssignmentSubmission


class CourseworkAPITestCase(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        provision_device()
        cls.facility = Facility.objects.create(name="Test Facility")
        cls.classroom = Classroom.objects.create(
            name="Biology 101", parent=cls.facility
        )

        cls.admin = FacilityUser.objects.create(username="admin", facility=cls.facility)
        cls.admin.set_password(DUMMY_PASSWORD)
        cls.admin.save()
        cls.facility.add_admin(cls.admin)

        cls.coach = FacilityUser.objects.create(username="coach", facility=cls.facility)
        cls.coach.set_password(DUMMY_PASSWORD)
        cls.coach.save()
        cls.classroom.add_coach(cls.coach)

        cls.learner1 = FacilityUser.objects.create(
            username="student1", facility=cls.facility
        )
        cls.learner1.set_password(DUMMY_PASSWORD)
        cls.learner1.save()
        Membership.objects.create(user=cls.learner1, collection=cls.classroom)

        cls.learner2 = FacilityUser.objects.create(
            username="student2", facility=cls.facility
        )
        cls.learner2.set_password(DUMMY_PASSWORD)
        cls.learner2.save()
        Membership.objects.create(user=cls.learner2, collection=cls.classroom)

    def _login(self, user):
        self.client.login(
            username=user.username, password=DUMMY_PASSWORD, facility=self.facility
        )

    def test_coach_can_create_and_list_assignment(self):
        self._login(self.coach)
        url = reverse("kolibri:core:assignment-list")
        payload = {
            "title": "Mitosis Lab Report",
            "description": "Please submit your lab observations.",
            "collection": self.classroom.id,
            "max_points": 100,
            "allow_file_upload": True,
            "allow_text_submission": True,
            "is_active": True,
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "Mitosis Lab Report")

        # Coach lists assignments
        list_res = self.client.get(url, {"collection": self.classroom.id})
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        results = (
            list_res.data
            if isinstance(list_res.data, list)
            else list_res.data.get("results", [])
        )
        self.assertEqual(len(results), 1)

    def test_learner_can_view_assignment_and_submit_homework(self):
        # Create assignment as coach
        assignment = Assignment.objects.create(
            title="Cell Structure Homework",
            collection=self.classroom,
            max_points=50,
            allow_text_submission=True,
            allow_file_upload=True,
            is_active=True,
            created_by=self.coach,
        )

        # Student 1 views assignment
        self._login(self.learner1)
        assignment_url = reverse(
            "kolibri:core:assignment-detail", kwargs={"pk": assignment.id}
        )
        res = self.client.get(assignment_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Cell Structure Homework")

        # Student 1 submits homework
        submission_url = reverse("kolibri:core:submission-list")
        test_file = SimpleUploadedFile(
            "mitosis.pdf", b"%PDF-1.4 test content", content_type="application/pdf"
        )
        sub_payload = {
            "assignment": assignment.id,
            "text_content": "Here is my cellular analysis and diagram notes.",
            "file_attachment": test_file,
        }
        sub_res = self.client.post(submission_url, sub_payload, format="multipart")
        self.assertEqual(sub_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sub_res.data["file_name"], "mitosis.pdf")
        self.assertEqual(sub_res.data["status"], "submitted")
        self.assertEqual(sub_res.data["learner_username"], "student1")

        # Student 2 cannot view Student 1's submission
        self._login(self.learner2)
        sub_detail_url = reverse(
            "kolibri:core:submission-detail", kwargs={"pk": sub_res.data["id"]}
        )
        get_res = self.client.get(sub_detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

        # Coach views submission and grades it
        self._login(self.coach)
        coach_get_res = self.client.get(sub_detail_url)
        self.assertEqual(coach_get_res.status_code, status.HTTP_200_OK)

        grade_url = reverse(
            "kolibri:core:submission-grade", kwargs={"pk": sub_res.data["id"]}
        )
        grade_res = self.client.post(
            grade_url, {"grade": 48.5, "feedback": "Excellent microscope detail!"}
        )
        self.assertEqual(grade_res.status_code, status.HTTP_200_OK)
        self.assertEqual(grade_res.data["grade"], 48.5)
        self.assertEqual(grade_res.data["status"], "graded")

        # Student 1 sees the grade and feedback
        self._login(self.learner1)
        student_check_res = self.client.get(sub_detail_url)
        self.assertEqual(student_check_res.status_code, status.HTTP_200_OK)
        self.assertEqual(student_check_res.data["grade"], 48.5)
        self.assertEqual(
            student_check_res.data["feedback"], "Excellent microscope detail!"
        )

    def test_gradebook_overview(self):
        assignment = Assignment.objects.create(
            title="Genetics Quiz",
            collection=self.classroom,
            max_points=100,
            is_active=True,
            created_by=self.coach,
        )
        AssignmentSubmission.objects.create(
            assignment=assignment,
            learner=self.learner1,
            grade=95.0,
            status="graded",
        )

        self._login(self.coach)
        gradebook_url = reverse("kolibri:core:assignment-gradebook")
        res = self.client.get(gradebook_url, {"collection": self.classroom.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["assignments"]), 1)
        self.assertEqual(len(res.data["learners"]), 2)

        learner1_entry = next(
            l for l in res.data["learners"] if l["username"] == "student1"
        )
        self.assertEqual(learner1_entry["total_earned"], 95.0)
        self.assertEqual(learner1_entry["percentage"], 95.0)

    def test_discussion_board_threads_and_replies(self):
        # Student 1 starts a discussion thread
        self._login(self.learner1)
        thread_url = reverse("kolibri:core:discussionthread-list")
        t_payload = {
            "title": "Question about chromosome count",
            "content": "Can someone clarify how meiosis II divides chromatids?",
            "collection": self.classroom.id,
        }
        t_res = self.client.post(thread_url, t_payload)
        self.assertEqual(t_res.status_code, status.HTTP_201_CREATED)
        thread_id = t_res.data["id"]

        # Coach replies and pins the thread
        self._login(self.coach)
        pin_url = reverse(
            "kolibri:core:discussionthread-toggle-pin", kwargs={"pk": thread_id}
        )
        pin_res = self.client.post(pin_url)
        self.assertEqual(pin_res.status_code, status.HTTP_200_OK)
        self.assertTrue(pin_res.data["is_pinned"])

        reply_url = reverse("kolibri:core:discussionreply-list")
        r_payload = {
            "thread": thread_id,
            "content": "In meiosis II, sister chromatids separate similarly to mitosis.",
        }
        r_res = self.client.post(reply_url, r_payload)
        self.assertEqual(r_res.status_code, status.HTTP_201_CREATED)
        reply_id = r_res.data["id"]

        # Coach endorses the reply
        endorse_url = reverse(
            "kolibri:core:discussionreply-endorse", kwargs={"pk": reply_id}
        )
        endorse_res = self.client.post(endorse_url)
        self.assertEqual(endorse_res.status_code, status.HTTP_200_OK)
        self.assertTrue(endorse_res.data["is_endorsed"])
