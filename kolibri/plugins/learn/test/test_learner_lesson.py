import uuid

from django.urls import reverse

from kolibri.core.auth.models import Classroom
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.models import LearnerGroup
from kolibri.core.auth.test.helpers import clear_process_cache
from kolibri.core.auth.test.helpers import KolibriAPITestCase as APITestCase
from kolibri.core.auth.test.helpers import provision_device
from kolibri.core.lessons.models import Lesson
from kolibri.core.lessons.models import LessonAssignment
from kolibri.core.logger.models import ContentSummaryLog
from kolibri.utils.time_utils import local_now


class LearnerLessonTestCase(APITestCase):
    databases = "__all__"

    def setUp(self):
        clear_process_cache()
        provision_device()
        self.facility = Facility.objects.create(name="My Facility")
        self.learner_user = FacilityUser.objects.create(
            username="learner", facility=self.facility
        )
        self.learner_user.set_password("password")
        self.learner_user.save()
        self.basename = "kolibri:kolibri.plugins.learn:learnerlesson"
        self.classroom = Classroom.objects.create(
            name="Own Classroom", parent=self.facility
        )
        self.classroom.add_member(self.learner_user)

    def test_must_be_authenticated(self):
        get_request = self.client.get(reverse(self.basename + "-list"))
        self.assertEqual(get_request.status_code, 403)

    def test_learner_can_access_own_lessons(self):
        own_lesson = Lesson.objects.create(
            title="Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=True,
        )
        LessonAssignment.objects.create(
            lesson=own_lesson, assigned_by=self.learner_user, collection=self.classroom
        )
        self.client.login(username="learner", password="password")
        get_request = self.client.get(
            reverse(self.basename + "-detail", kwargs={"pk": own_lesson.id})
        )
        self.assertEqual(get_request.data["id"], own_lesson.id)

    def test_learner_cannot_access_not_own_lessons(self):
        # Lesson created in Classroom, but not assigned
        other_classroom = Classroom.objects.create(
            name="Other Classroom", parent=self.facility
        )
        other_lesson = Lesson.objects.create(
            title="Lesson",
            collection=other_classroom,
            created_by=self.learner_user,
            is_active=True,
        )
        LessonAssignment.objects.create(
            lesson=other_lesson,
            assigned_by=self.learner_user,
            collection=other_classroom,
        )
        self.client.login(username="learner", password="password")
        get_request = self.client.get(
            reverse(self.basename + "-detail", kwargs={"pk": other_lesson.id})
        )
        self.assertEqual(get_request.status_code, 404)

    def test_learner_cannot_access_own_inactive_lesson(self):
        own_lesson = Lesson.objects.create(
            title="Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=False,
        )
        LessonAssignment.objects.create(
            lesson=own_lesson, assigned_by=self.learner_user, collection=self.classroom
        )
        self.client.login(username="learner", password="password")
        get_request = self.client.get(
            reverse(self.basename + "-detail", kwargs={"pk": own_lesson.id})
        )
        self.assertEqual(get_request.status_code, 404)

    def test_learner_assigned_same_lesson_multiple_times_only_return_one(self):
        own_lesson = Lesson.objects.create(
            title="Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=True,
        )
        LessonAssignment.objects.create(
            lesson=own_lesson, assigned_by=self.learner_user, collection=self.classroom
        )
        group = LearnerGroup.objects.create(name="Own Group", parent=self.classroom)
        group.add_member(self.learner_user)
        LessonAssignment.objects.create(
            lesson=own_lesson, assigned_by=self.learner_user, collection=group
        )
        self.client.login(username="learner", password="password")
        get_request = self.client.get(
            reverse(self.basename + "-detail", kwargs={"pk": own_lesson.id})
        )
        self.assertEqual(get_request.status_code, 200)

    def test_response_shape_includes_classroom_nested_object(self):
        # Lesson.resources has default=[] so it doesn't need to be specified here.
        own_lesson = Lesson.objects.create(
            title="Shape Test Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=True,
        )
        LessonAssignment.objects.create(
            lesson=own_lesson, assigned_by=self.learner_user, collection=self.classroom
        )
        self.client.login(username="learner", password="password")
        response = self.client.get(
            reverse(self.basename + "-detail", kwargs={"pk": own_lesson.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        # Top-level fields
        self.assertEqual(data["id"], own_lesson.id)
        self.assertEqual(data["title"], "Shape Test Lesson")
        self.assertIn("description", data)
        self.assertIn("resources", data)
        self.assertIn("collection", data)
        # consolidate() renames is_active → active; is_active must not appear
        self.assertIn("active", data)
        self.assertNotIn("is_active", data)
        # consolidate() adds progress and missing_resource (even with empty resources)
        self.assertIn("progress", data)
        self.assertIn("missing_resource", data)
        # classroom nested object
        classroom = data["classroom"]
        self.assertEqual(classroom["id"], str(self.classroom.id))
        self.assertEqual(classroom["name"], "Own Classroom")
        self.assertEqual(classroom["parent"], str(self.classroom.parent.id))

    def test_learner_custom_resource_progress_tracking(self):
        res1_id = uuid.uuid4().hex
        res2_id = uuid.uuid4().hex
        custom_lesson = Lesson.objects.create(
            title="Custom Progress Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=True,
            resources=[
                {
                    "content_id": res1_id,
                    "contentnode_id": uuid.uuid4().hex,
                    "channel_id": "custom",
                    "is_custom": True,
                    "resource_type": "youtube",
                    "title": "Custom YouTube",
                },
                {
                    "content_id": res2_id,
                    "contentnode_id": uuid.uuid4().hex,
                    "channel_id": "custom",
                    "is_custom": True,
                    "resource_type": "pdf",
                    "title": "Custom PDF",
                },
            ],
        )
        LessonAssignment.objects.create(
            lesson=custom_lesson,
            assigned_by=self.learner_user,
            collection=self.classroom,
        )
        self.client.login(username="learner", password="password")

        # Initially 0 progress
        res = self.client.get(
            reverse(self.basename + "-detail", kwargs={"pk": custom_lesson.id})
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["progress"]["resource_progress"], 0)
        self.assertEqual(res.data["resources"][0]["progress"], 0)
        self.assertEqual(res.data["resources"][1]["progress"], 0)

        # Learner completes resource 1 (progress=1.0) and starts resource 2 (progress=0.5)
        ContentSummaryLog.objects.create(
            user=self.learner_user,
            content_id=res1_id,
            progress=1.0,
            kind="video",
            start_timestamp=local_now(),
            completion_timestamp=local_now(),
        )
        ContentSummaryLog.objects.create(
            user=self.learner_user,
            content_id=res2_id,
            progress=0.5,
            kind="document",
            start_timestamp=local_now(),
        )

        # Re-fetch lesson: progress is accurately computed
        res = self.client.get(
            reverse(self.basename + "-detail", kwargs={"pk": custom_lesson.id})
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["resources"][0]["progress"], 1.0)
        self.assertEqual(res.data["resources"][1]["progress"], 0.5)
        self.assertAlmostEqual(res.data["progress"]["resource_progress"], 1.5)

    def test_learner_classroom_custom_resource_progress(self):
        res1_id = uuid.uuid4().hex
        custom_lesson = Lesson.objects.create(
            title="Classroom Custom Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=True,
            resources=[
                {
                    "content_id": res1_id,
                    "contentnode_id": uuid.uuid4().hex,
                    "channel_id": "custom",
                    "is_custom": True,
                    "resource_type": "youtube",
                    "title": "Custom Video",
                }
            ],
        )
        LessonAssignment.objects.create(
            lesson=custom_lesson,
            assigned_by=self.learner_user,
            collection=self.classroom,
        )
        ContentSummaryLog.objects.create(
            user=self.learner_user,
            content_id=res1_id,
            progress=1.0,
            kind="video",
            start_timestamp=local_now(),
            completion_timestamp=local_now(),
        )

        self.client.login(username="learner", password="password")
        classroom_url = reverse("kolibri:kolibri.plugins.learn:learnerclassroom-list")
        res = self.client.get(classroom_url)
        self.assertEqual(res.status_code, 200)
        classroom_data = res.data[0]
        matching_lesson = next(
            l for l in classroom_data["lessons"] if l["id"] == custom_lesson.id
        )
        self.assertEqual(matching_lesson["progress"]["resource_progress"], 1.0)
        self.assertEqual(matching_lesson["resources"][0]["progress"], 1.0)

    def test_update_custom_progress_marks_started_and_completed(self):
        res_id = uuid.uuid4().hex
        node_id = uuid.uuid4().hex
        custom_lesson = Lesson.objects.create(
            title="Interactive Progress Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=True,
            resources=[
                {
                    "content_id": res_id,
                    "contentnode_id": node_id,
                    "channel_id": "custom",
                    "is_custom": True,
                    "resource_type": "h5p",
                    "title": "Math H5P Activity",
                }
            ],
        )
        LessonAssignment.objects.create(
            lesson=custom_lesson,
            assigned_by=self.learner_user,
            collection=self.classroom,
        )
        self.client.login(username="learner", password="password")
        url = reverse(
            self.basename + "-update_custom_progress",
            kwargs={"pk": custom_lesson.id},
        )

        # 1. Post initial started progress
        start_res = self.client.post(
            url,
            data={"content_id": res_id, "progress": 0.1, "time_spent": 15},
            format="json",
        )
        self.assertEqual(start_res.status_code, 200)
        self.assertEqual(start_res.data["progress"], 0.1)
        self.assertEqual(start_res.data["time_spent"], 15.0)

        log = ContentSummaryLog.objects.get(user=self.learner_user, content_id=res_id)
        self.assertEqual(log.progress, 0.1)
        self.assertEqual(log.time_spent, 15.0)
        self.assertEqual(log.kind, "html5")
        self.assertIsNone(log.completion_timestamp)

        # 2. Post completed progress with additional time spent
        finish_res = self.client.post(
            url,
            data={"content_id": res_id, "progress": 1.0, "time_spent": 45},
            format="json",
        )
        self.assertEqual(finish_res.status_code, 200)
        self.assertEqual(finish_res.data["progress"], 1.0)
        self.assertEqual(finish_res.data["time_spent"], 60.0)

        log.refresh_from_db()
        self.assertEqual(log.progress, 1.0)
        self.assertEqual(log.time_spent, 60.0)
        self.assertIsNotNone(log.completion_timestamp)

    def test_update_custom_progress_invalid_resource_returns_404(self):
        custom_lesson = Lesson.objects.create(
            title="Empty Custom Lesson",
            collection=self.classroom,
            created_by=self.learner_user,
            is_active=True,
            resources=[],
        )
        LessonAssignment.objects.create(
            lesson=custom_lesson,
            assigned_by=self.learner_user,
            collection=self.classroom,
        )
        self.client.login(username="learner", password="password")
        url = reverse(
            self.basename + "-update_custom_progress",
            kwargs={"pk": custom_lesson.id},
        )
        res = self.client.post(
            url,
            data={"content_id": uuid.uuid4().hex, "progress": 1.0},
            format="json",
        )
        self.assertEqual(res.status_code, 404)
