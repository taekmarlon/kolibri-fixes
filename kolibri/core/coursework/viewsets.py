import logging

from django.db.models import Count
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.serializers import CharField
from rest_framework.serializers import FileField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import ValidationError

from kolibri.core.api import ValuesViewset
from kolibri.core.auth.constants import role_kinds
from kolibri.core.auth.models import Collection
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.permissions import _ensure_raw_dict
from kolibri.core.auth.permissions import KolibriAuthPermissions
from kolibri.core.auth.permissions import KolibriAuthPermissionsFilter
from kolibri.core.coursework.models import Assignment
from kolibri.core.coursework.models import AssignmentSubmission
from kolibri.core.coursework.models import DiscussionReply
from kolibri.core.coursework.models import DiscussionThread
from kolibri.core.serializers import DateTimeTzField
from kolibri.core.utils.pagination import OptionalPageNumberPagination
from kolibri.utils.time_utils import local_now

logger = logging.getLogger(__name__)


class CourseworkAuthPermissions(KolibriAuthPermissions):
    def has_permission(self, request, view):
        if (
            getattr(view, "action", None) == "create"
            and request.method == "POST"
            and request.data
        ):
            if type(request.data) is list:
                data = request.data
            else:
                data = [request.data]
            return all(self.validator(request, view, datum) for datum in data)
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "OPTIONS", "HEAD"]:
            return request.user.can_read(obj)
        if request.method in ["PUT", "PATCH", "POST"]:
            return request.user.can_update(obj)
        if request.method == "DELETE":
            return request.user.can_delete(obj)
        return False


# -------------------------------------------------------------------------
# Assignments
# -------------------------------------------------------------------------


class AssignmentSerializer(ModelSerializer):
    collection = PrimaryKeyRelatedField(queryset=Collection.objects.all())
    collection_name = CharField(source="collection__name", read_only=True)
    created_by = PrimaryKeyRelatedField(read_only=True)
    created_by_username = CharField(source="created_by__username", read_only=True)
    due_date = DateTimeTzField(required=False, allow_null=True)
    video_url = CharField(required=False, allow_blank=True)
    date_created = DateTimeTzField(read_only=True)
    date_modified = DateTimeTzField(read_only=True)
    submissions_count = IntegerField(read_only=True)
    graded_count = IntegerField(read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "description",
            "collection",
            "collection_name",
            "due_date",
            "max_points",
            "allow_file_upload",
            "allow_text_submission",
            "video_url",
            "is_active",
            "created_by",
            "created_by_username",
            "date_created",
            "date_modified",
            "submissions_count",
            "graded_count",
        )

    def validate(self, attrs):
        if not self.instance and "request" in self.context:
            attrs["created_by"] = self.context["request"].user
        return attrs


class AssignmentViewSet(ValuesViewset):
    serializer_class = AssignmentSerializer
    permission_classes = (CourseworkAuthPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter, DjangoFilterBackend)
    filterset_fields = ("collection", "is_active")
    pagination_class = OptionalPageNumberPagination

    def annotate_queryset(self, queryset):
        return queryset.annotate(
            submissions_count=Count("submissions", distinct=True),
            graded_count=Count(
                "submissions", filter=Q(submissions__status="graded"), distinct=True
            ),
        )

    def get_queryset(self):
        return Assignment.objects.order_by("-date_created")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def gradebook(self, request):
        """
        Returns full gradebook data for a classroom collection:
        List of learners, list of assignments, and each learner's submission scores & stats.
        """
        collection_id = request.query_params.get("collection")
        if not collection_id:
            return Response(
                {"error": "collection parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            collection = Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            return Response(
                {"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), collection
        ):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        assignments = Assignment.objects.filter(
            collection=collection, is_active=True
        ).order_by("date_created")
        learners = FacilityUser.objects.filter(
            memberships__collection=collection
        ).order_by("full_name", "username")
        submissions = AssignmentSubmission.objects.filter(
            assignment__collection=collection
        )

        submissions_map = {
            f"{s.assignment_id}:{s.learner_id}": {
                "id": s.id,
                "status": s.status,
                "grade": s.grade,
                "submitted_at": s.submitted_at,
                "file_name": s.file_name,
                "has_file": bool(s.file_attachment),
                "feedback": s.feedback,
            }
            for s in submissions
        }

        learners_data = []
        for learner in learners:
            learner_subs = {}
            total_earned = 0.0
            total_possible = 0.0
            completed_count = 0

            for a in assignments:
                sub = submissions_map.get(f"{a.id}:{learner.id}")
                learner_subs[a.id] = sub
                if sub and sub["grade"] is not None:
                    total_earned += sub["grade"]
                    total_possible += a.max_points
                    completed_count += 1
                elif sub and sub["status"] == "submitted":
                    completed_count += 1

            percentage = (
                round((total_earned / total_possible * 100), 1)
                if total_possible > 0
                else None
            )
            learners_data.append(
                {
                    "id": learner.id,
                    "username": learner.username,
                    "full_name": learner.full_name,
                    "submissions": learner_subs,
                    "total_earned": total_earned,
                    "total_possible": total_possible,
                    "percentage": percentage,
                    "completed_assignments": completed_count,
                }
            )

        assignments_data = [
            {
                "id": a.id,
                "title": a.title,
                "max_points": a.max_points,
                "due_date": a.due_date,
            }
            for a in assignments
        ]

        return Response(
            {
                "classroom_id": collection.id,
                "classroom_name": collection.name,
                "assignments": assignments_data,
                "learners": learners_data,
            }
        )


# -------------------------------------------------------------------------
# Submissions
# -------------------------------------------------------------------------


class AssignmentSubmissionSerializer(ModelSerializer):
    assignment = PrimaryKeyRelatedField(queryset=Assignment.objects.all())
    assignment_title = CharField(source="assignment__title", read_only=True)
    assignment_max_points = IntegerField(
        source="assignment__max_points", read_only=True
    )
    learner = PrimaryKeyRelatedField(read_only=True)
    learner_username = CharField(source="learner__username", read_only=True)
    learner_full_name = CharField(source="learner__full_name", read_only=True)
    file_attachment = FileField(required=False, allow_null=True)
    graded_by = PrimaryKeyRelatedField(read_only=True)
    graded_by_username = CharField(source="graded_by__username", read_only=True)
    submitted_at = DateTimeTzField(read_only=True)
    graded_at = DateTimeTzField(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = (
            "id",
            "assignment",
            "assignment_title",
            "assignment_max_points",
            "learner",
            "learner_username",
            "learner_full_name",
            "text_content",
            "file_attachment",
            "file_name",
            "file_size",
            "status",
            "grade",
            "feedback",
            "graded_by",
            "graded_by_username",
            "submitted_at",
            "graded_at",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        if not self.instance:
            if request and request.user.is_authenticated:
                attrs["learner"] = request.user
            assignment = attrs.get("assignment")
            if assignment:
                if not assignment.is_active:
                    raise ValidationError("Assignment is not active.")
                if not request.user.is_member_of(assignment.collection):
                    raise ValidationError("You are not enrolled in this classroom.")
        return attrs

    def create(self, validated_data):
        file_obj = validated_data.get("file_attachment")
        if file_obj and hasattr(file_obj, "name"):
            validated_data["file_name"] = file_obj.name
            validated_data["file_size"] = getattr(file_obj, "size", 0)

        validated_data["submitted_at"] = local_now()
        validated_data["status"] = "submitted"

        assignment = validated_data.pop("assignment")
        learner = validated_data.pop("learner")

        submission, _ = AssignmentSubmission.objects.update_or_create(
            assignment=assignment,
            learner=learner,
            defaults=validated_data,
        )
        return submission

    def update(self, instance, validated_data):
        file_obj = validated_data.get("file_attachment")
        if file_obj and hasattr(file_obj, "name"):
            validated_data["file_name"] = file_obj.name
            validated_data["file_size"] = getattr(file_obj, "size", 0)

        validated_data["submitted_at"] = local_now()
        return super().update(instance, validated_data)


class AssignmentSubmissionPermissions(CourseworkAuthPermissions):
    def validator(self, request, view, datum):
        if request.user.is_anonymous:
            return False
        model = view.get_serializer_class().Meta.model
        datum = _ensure_raw_dict(datum)
        validated_data = view.get_serializer().to_internal_value(datum)
        validated_data["learner"] = request.user
        return request.user.can_create(model, validated_data)


class AssignmentSubmissionViewSet(ValuesViewset):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = (AssignmentSubmissionPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter, DjangoFilterBackend)
    filterset_fields = ("assignment", "learner", "status")
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        return AssignmentSubmission.objects.order_by("-submitted_at")

    @action(detail=True, methods=["post"])
    def grade(self, request, pk=None):
        """
        Endpoint for coach to grade a submission and post feedback.
        """
        submission = self.get_object()
        classroom = submission.assignment.collection
        if not request.user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), classroom
        ):
            return Response(
                {"error": "Only coaches can grade submissions"},
                status=status.HTTP_403_FORBIDDEN,
            )

        grade_val = request.data.get("grade")
        feedback_val = request.data.get("feedback", "")

        if grade_val is not None:
            try:
                grade_val = float(grade_val)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid grade number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        submission.grade = grade_val
        submission.feedback = feedback_val
        submission.status = "graded"
        submission.graded_by = request.user
        submission.graded_at = local_now()
        submission.save()

        return Response(self.serialize_object(pk=submission.pk))


# -------------------------------------------------------------------------
# Discussions
# -------------------------------------------------------------------------


class DiscussionReplySerializer(ModelSerializer):
    thread = PrimaryKeyRelatedField(queryset=DiscussionThread.objects.all())
    created_by = PrimaryKeyRelatedField(read_only=True)
    created_by_username = CharField(source="created_by__username", read_only=True)
    created_by_full_name = CharField(source="created_by__full_name", read_only=True)
    date_created = DateTimeTzField(read_only=True)

    class Meta:
        model = DiscussionReply
        fields = (
            "id",
            "thread",
            "content",
            "is_endorsed",
            "created_by",
            "created_by_username",
            "created_by_full_name",
            "date_created",
        )

    def validate(self, attrs):
        if not self.instance and "request" in self.context:
            attrs["created_by"] = self.context["request"].user
        return attrs


class DiscussionReplyPermissions(CourseworkAuthPermissions):
    def validator(self, request, view, datum):
        if request.user.is_anonymous:
            return False
        model = view.get_serializer_class().Meta.model
        datum = _ensure_raw_dict(datum)
        validated_data = view.get_serializer().to_internal_value(datum)
        validated_data["created_by"] = request.user
        return request.user.can_create(model, validated_data)


class DiscussionReplyViewSet(ValuesViewset):
    serializer_class = DiscussionReplySerializer
    permission_classes = (DiscussionReplyPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter, DjangoFilterBackend)
    filterset_fields = ("thread", "is_endorsed")
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        return DiscussionReply.objects.order_by("date_created")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def endorse(self, request, pk=None):
        reply = self.get_object()
        classroom = reply.thread.collection
        if not request.user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), classroom
        ):
            return Response(
                {"error": "Only coaches can endorse replies"},
                status=status.HTTP_403_FORBIDDEN,
            )

        reply.is_endorsed = not reply.is_endorsed
        reply.save()
        return Response({"is_endorsed": reply.is_endorsed})


class DiscussionThreadSerializer(ModelSerializer):
    collection = PrimaryKeyRelatedField(queryset=Collection.objects.all())
    created_by = PrimaryKeyRelatedField(read_only=True)
    created_by_username = CharField(source="created_by__username", read_only=True)
    created_by_full_name = CharField(source="created_by__full_name", read_only=True)
    date_created = DateTimeTzField(read_only=True)
    date_modified = DateTimeTzField(read_only=True)
    reply_count = IntegerField(read_only=True)

    class Meta:
        model = DiscussionThread
        fields = (
            "id",
            "title",
            "content",
            "collection",
            "is_pinned",
            "is_closed",
            "created_by",
            "created_by_username",
            "created_by_full_name",
            "date_created",
            "date_modified",
            "reply_count",
        )

    def validate(self, attrs):
        if not self.instance and "request" in self.context:
            attrs["created_by"] = self.context["request"].user
        return attrs


class DiscussionThreadPermissions(CourseworkAuthPermissions):
    def validator(self, request, view, datum):
        if request.user.is_anonymous:
            return False
        model = view.get_serializer_class().Meta.model
        datum = _ensure_raw_dict(datum)
        validated_data = view.get_serializer().to_internal_value(datum)
        validated_data["created_by"] = request.user
        return request.user.can_create(model, validated_data)


class DiscussionThreadViewSet(ValuesViewset):
    serializer_class = DiscussionThreadSerializer
    permission_classes = (DiscussionThreadPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter, DjangoFilterBackend)
    filterset_fields = ("collection", "is_pinned", "is_closed")
    pagination_class = OptionalPageNumberPagination

    def annotate_queryset(self, queryset):
        return queryset.annotate(reply_count=Count("replies", distinct=True))

    def get_queryset(self):
        return DiscussionThread.objects.order_by("-is_pinned", "-date_created")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle_pin(self, request, pk=None):
        thread = self.get_object()
        if not request.user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), thread.collection
        ):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        thread.is_pinned = not thread.is_pinned
        thread.save()
        return Response({"is_pinned": thread.is_pinned})

    @action(detail=True, methods=["post"])
    def toggle_close(self, request, pk=None):
        thread = self.get_object()
        if not request.user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), thread.collection
        ):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        thread.is_closed = not thread.is_closed
        thread.save()
        return Response({"is_closed": thread.is_closed})
