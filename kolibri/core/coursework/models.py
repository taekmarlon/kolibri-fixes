import os
import uuid

from django.db import models

from kolibri.core.auth.constants import role_kinds
from kolibri.core.auth.models import AbstractFacilityDataModel
from kolibri.core.auth.models import Collection
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.permissions.base import RoleBasedPermissions
from kolibri.core.coursework.permissions import AssignmentSubmissionPermissions
from kolibri.core.coursework.permissions import DiscussionReplyPermissions
from kolibri.core.coursework.permissions import DiscussionThreadPermissions
from kolibri.core.coursework.permissions import UserCanReadAssignment
from kolibri.core.fields import DateTimeTzField
from kolibri.utils.time_utils import local_now


def submission_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    safe_name = f"{uuid.uuid4()}{ext}"
    return os.path.join("coursework", "submissions", safe_name)


class Assignment(AbstractFacilityDataModel):
    """
    An Assignment represents homework, a project, lab report, or problem set
    assigned to a Classroom.
    """

    morango_model_name = "assignment"

    permissions = (
        RoleBasedPermissions(
            target_field="collection",
            can_be_created_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_read_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_updated_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_deleted_by=(role_kinds.ADMIN, role_kinds.COACH),
        )
        | UserCanReadAssignment()
    )

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    collection = models.ForeignKey(
        Collection,
        related_name="assignments",
        on_delete=models.CASCADE,
    )
    due_date = DateTimeTzField(null=True, blank=True)
    max_points = models.PositiveIntegerField(default=100)
    allow_file_upload = models.BooleanField(default=True)
    allow_text_submission = models.BooleanField(default=True)
    video_url = models.URLField(blank=True, default="", max_length=500)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        FacilityUser,
        related_name="assignments_created",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    date_created = DateTimeTzField(default=local_now, editable=False)
    date_modified = DateTimeTzField(default=local_now)

    class Meta:
        ordering = ["-date_created"]

    def __str__(self):
        return f"Assignment: {self.title} for {self.collection.name}"

    def pre_save(self, **kwargs):
        super().pre_save(**kwargs)
        self.enforce_authoring_user_field("created_by", **kwargs)

    def infer_dataset(self, *args, **kwargs):
        return self.cached_related_dataset_lookup("collection")

    def calculate_partition(self):
        return self.dataset_id


class AssignmentSubmission(AbstractFacilityDataModel):
    """
    A Learner's submission for an Assignment.
    """

    morango_model_name = "assignmentsubmission"

    permissions = AssignmentSubmissionPermissions()

    assignment = models.ForeignKey(
        Assignment,
        related_name="submissions",
        on_delete=models.CASCADE,
    )
    learner = models.ForeignKey(
        FacilityUser,
        related_name="assignment_submissions",
        on_delete=models.CASCADE,
    )
    text_content = models.TextField(blank=True, default="")
    file_attachment = models.FileField(
        upload_to=submission_file_path, null=True, blank=True
    )
    file_name = models.CharField(max_length=255, blank=True, default="")
    file_size = models.BigIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=(
            ("submitted", "Submitted"),
            ("graded", "Graded"),
            ("returned", "Returned"),
        ),
        default="submitted",
    )
    grade = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, default="")
    graded_by = models.ForeignKey(
        FacilityUser,
        related_name="submissions_graded",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    submitted_at = DateTimeTzField(default=local_now)
    graded_at = DateTimeTzField(null=True, blank=True)

    class Meta:
        unique_together = (("assignment", "learner"),)
        ordering = ["-submitted_at"]

    @property
    def collection(self):
        return self.assignment.collection

    def __str__(self):
        return f"Submission by {self.learner.username} for {self.assignment.title}"

    def calculate_source_id(self):
        return f"{self.assignment_id}:{self.learner_id}"

    def infer_dataset(self, *args, **kwargs):
        return self.cached_related_dataset_lookup("assignment")

    def calculate_partition(self):
        return self.dataset_id


class DiscussionThread(AbstractFacilityDataModel):
    """
    A discussion thread or Q&A topic within a Classroom.
    """

    morango_model_name = "discussionthread"

    permissions = DiscussionThreadPermissions()

    collection = models.ForeignKey(
        Collection,
        related_name="discussion_threads",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(
        FacilityUser,
        related_name="discussion_threads_created",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    date_created = DateTimeTzField(default=local_now, editable=False)
    date_modified = DateTimeTzField(default=local_now)

    class Meta:
        ordering = ["-is_pinned", "-date_created"]

    def __str__(self):
        return f"Thread: {self.title} in {self.collection.name}"

    def pre_save(self, **kwargs):
        super().pre_save(**kwargs)
        self.enforce_authoring_user_field("created_by", **kwargs)

    def infer_dataset(self, *args, **kwargs):
        return self.cached_related_dataset_lookup("collection")

    def calculate_partition(self):
        return self.dataset_id


class DiscussionReply(AbstractFacilityDataModel):
    """
    A reply to a DiscussionThread.
    """

    morango_model_name = "discussionreply"

    permissions = DiscussionReplyPermissions()

    thread = models.ForeignKey(
        DiscussionThread,
        related_name="replies",
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        FacilityUser,
        related_name="discussion_replies_created",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    is_endorsed = models.BooleanField(default=False)
    date_created = DateTimeTzField(default=local_now, editable=False)

    class Meta:
        ordering = ["date_created"]

    @property
    def collection(self):
        return self.thread.collection

    def __str__(self):
        return f"Reply by {self.created_by.username if self.created_by else 'Unknown'} to {self.thread.title}"

    def pre_save(self, **kwargs):
        super().pre_save(**kwargs)
        self.enforce_authoring_user_field("created_by", **kwargs)

    def infer_dataset(self, *args, **kwargs):
        return self.cached_related_dataset_lookup("thread")

    def calculate_partition(self):
        return self.dataset_id
