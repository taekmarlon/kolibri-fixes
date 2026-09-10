import logging

from django.db.models import Count
from django.db.models import Max
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.serializers import CharField
from rest_framework.serializers import FileField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import JSONField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import ValidationError

from kolibri.core.api import ValuesViewset
from kolibri.core.attendance.models import AttendanceRecord
from kolibri.core.attendance.models import AttendanceSession
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
from kolibri.core.coursework.models import LearnerIntervention
from kolibri.core.exams.models import Exam
from kolibri.core.logger.models import AttemptLog
from kolibri.core.logger.models import ContentSummaryLog
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

        file_obj = attrs.get("file_attachment")
        if file_obj and hasattr(file_obj, "size"):
            # DepEd / System constraint: 5 MB maximum file size allowed
            if file_obj.size > 5 * 1024 * 1024:
                raise ValidationError(
                    {"file_attachment": "File size exceeds the 5 MB maximum limit."}
                )
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


# -------------------------------------------------------------------------
# Learner Interventions (Early Warning System)
# -------------------------------------------------------------------------


class LearnerInterventionPermissions(CourseworkAuthPermissions):
    def validator(self, request, view, datum):
        model = view.get_serializer_class().Meta.model
        datum = _ensure_raw_dict(datum)
        validated_data = view.get_serializer().to_internal_value(datum)
        validated_data["coach"] = request.user
        return request.user.can_create(model, validated_data)


class LearnerInterventionSerializer(ModelSerializer):
    collection = PrimaryKeyRelatedField(queryset=Collection.objects.all())
    collection_name = CharField(source="collection__name", read_only=True)
    learner = PrimaryKeyRelatedField(queryset=FacilityUser.objects.all())
    learner_name = CharField(source="learner__full_name", read_only=True)
    learner_username = CharField(source="learner__username", read_only=True)
    coach = PrimaryKeyRelatedField(read_only=True)
    coach_name = CharField(source="coach__full_name", read_only=True)
    coach_username = CharField(source="coach__username", read_only=True)
    reasons = JSONField(default=list, required=False)

    class Meta:
        model = LearnerIntervention
        fields = (
            "id",
            "collection",
            "collection_name",
            "learner",
            "learner_name",
            "learner_username",
            "coach",
            "coach_name",
            "coach_username",
            "risk_level",
            "reasons",
            "intervention_type",
            "notes",
            "status",
            "target_date",
            "date_created",
            "date_modified",
        )
        read_only_fields = ("id", "coach", "date_created", "date_modified")

    def validate(self, attrs):
        if not self.instance and "request" in self.context:
            attrs["coach"] = self.context["request"].user
        return attrs


class LearnerInterventionViewSet(ValuesViewset):
    serializer_class = LearnerInterventionSerializer
    permission_classes = (LearnerInterventionPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter, DjangoFilterBackend)
    filterset_fields = (
        "collection",
        "learner",
        "risk_level",
        "status",
        "intervention_type",
    )
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        return LearnerIntervention.objects.order_by("-date_created")

    def perform_create(self, serializer):
        serializer.save(coach=self.request.user)


# -------------------------------------------------------------------------
# At-Risk Analytics (Early Warning System)
# -------------------------------------------------------------------------


class AtRiskAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_user_attendance(self, collection, learners, total_sessions):
        attendance_records = AttendanceRecord.objects.filter(
            attendance_session__collection=collection,
            user__in=learners,
        ).values("user_id", "present")

        user_attendance = {
            l.id: {"present": 0, "absent": 0, "rate": 100.0} for l in learners
        }
        for rec in attendance_records:
            uid = rec["user_id"]
            if uid in user_attendance:
                if rec["present"]:
                    user_attendance[uid]["present"] += 1
                else:
                    user_attendance[uid]["absent"] += 1

        for uid, att in user_attendance.items():
            if total_sessions > 0:
                att["rate"] = round((att["present"] / total_sessions) * 100, 1)
        return user_attendance

    def _get_user_quiz_stats(self, collection, learners):
        exams = Exam.objects.filter(collection=collection)
        user_quiz_stats = {l.id: {"total_quizzes": 0, "scores": []} for l in learners}
        for exam in exams:
            for l in learners:
                user_logs = AttemptLog.objects.filter(
                    masterylog__summarylog__content_id=exam.id,
                    user=l,
                )
                if user_logs.exists():
                    total_q = user_logs.values("item").distinct().count()
                    correct_q = (
                        user_logs.filter(correct=1).values("item").distinct().count()
                    )
                    if total_q > 0:
                        pct = round((correct_q / total_q) * 100, 1)
                        user_quiz_stats[l.id]["scores"].append(pct)
                        user_quiz_stats[l.id]["total_quizzes"] += 1
        return user_quiz_stats

    def _get_user_cw_stats(self, collection, learners):
        submissions = AssignmentSubmission.objects.filter(
            assignment__collection=collection,
            learner__in=learners,
        ).values(
            "learner_id", "assignment_id", "status", "grade", "assignment__max_points"
        )

        user_cw_stats = {l.id: {"submitted_ids": set(), "grades": []} for l in learners}
        for sub in submissions:
            lid = sub["learner_id"]
            if lid in user_cw_stats:
                user_cw_stats[lid]["submitted_ids"].add(sub["assignment_id"])
                if sub["status"] == "graded" and sub["grade"] is not None:
                    max_pts = sub["assignment__max_points"] or 100
                    pct = round((sub["grade"] / max_pts) * 100, 1)
                    user_cw_stats[lid]["grades"].append(pct)
        return user_cw_stats

    def _get_user_last_activity(self, collection, learners):
        user_last_activity = {}
        for l in learners:
            latest_cw = AssignmentSubmission.objects.filter(
                assignment__collection=collection, learner=l
            ).aggregate(Max("submitted_at"))["submitted_at__max"]
            latest_content = ContentSummaryLog.objects.filter(user=l).aggregate(
                Max("end_timestamp")
            )["end_timestamp__max"]
            dates = [d for d in [latest_cw, latest_content] if d is not None]
            user_last_activity[l.id] = max(dates) if dates else None
        return user_last_activity

    def _get_user_interventions(self, collection, learners):
        interventions = LearnerIntervention.objects.filter(
            collection=collection, learner__in=learners
        ).order_by("-date_created")
        user_interventions = {l.id: [] for l in learners}
        for itv in interventions:
            user_interventions[itv.learner_id].append(
                {
                    "id": str(itv.id),
                    "risk_level": itv.risk_level,
                    "reasons": itv.reasons,
                    "intervention_type": itv.intervention_type,
                    "notes": itv.notes,
                    "status": itv.status,
                    "target_date": itv.target_date,
                    "coach_name": itv.coach.full_name or itv.coach.username,
                    "date_created": itv.date_created,
                }
            )
        return user_interventions

    def _analyze_factors(
        self, att, total_sessions, q_stats, cw, total_assignments, last_act, now
    ):
        factors = []
        if total_sessions >= 2 and att["rate"] < 80.0:
            factors.append(
                {
                    "category": "attendance",
                    "severity": "high" if att["rate"] < 60.0 else "moderate",
                    "label": f"Low Attendance ({att['rate']}%)",
                    "detail": f"Attended {att['present']} of {total_sessions} sessions (Below 80% threshold)",
                }
            )

        avg_quiz = None
        if q_stats["scores"]:
            avg_quiz = round(sum(q_stats["scores"]) / len(q_stats["scores"]), 1)
            if avg_quiz < 75.0:
                factors.append(
                    {
                        "category": "academic",
                        "severity": "high" if avg_quiz < 60.0 else "moderate",
                        "label": f"Failing Quiz Average ({avg_quiz}%)",
                        "detail": f"Average score across {len(q_stats['scores'])} quizzes is {avg_quiz}% (Below 75% DepEd passing standard)",
                    }
                )

        missing_count = total_assignments - len(cw["submitted_ids"])
        if total_assignments > 0 and missing_count >= 2:
            factors.append(
                {
                    "category": "missing_work",
                    "severity": "high" if missing_count >= 3 else "moderate",
                    "label": f"{missing_count} Missing Assignments",
                    "detail": f"Has not submitted {missing_count} of {total_assignments} active assignments",
                }
            )
        elif cw["grades"]:
            avg_hw = round(sum(cw["grades"]) / len(cw["grades"]), 1)
            if avg_hw < 75.0:
                factors.append(
                    {
                        "category": "academic_hw",
                        "severity": "moderate",
                        "label": f"Low Homework Score ({avg_hw}%)",
                        "detail": f"Average coursework grade is {avg_hw}% (Below 75% threshold)",
                    }
                )

        days_inactive = (now - last_act).days if last_act else None
        if days_inactive is not None and days_inactive >= 7:
            factors.append(
                {
                    "category": "inactivity",
                    "severity": "high" if days_inactive >= 14 else "moderate",
                    "label": f"Inactive for {days_inactive} days",
                    "detail": f"Last activity was {days_inactive} days ago",
                }
            )
        elif last_act is None and (total_sessions > 0 or total_assignments > 0):
            factors.append(
                {
                    "category": "inactivity",
                    "severity": "high",
                    "label": "No Recorded Activity",
                    "detail": "Learner has not logged in or interacted with class content",
                }
            )
        return factors, avg_quiz, missing_count

    def list(self, request):
        collection_id = request.query_params.get("collection")
        if not collection_id:
            return Response(
                {"error": "collection query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            collection = Collection.objects.get(id=collection_id)
        except (Collection.DoesNotExist, ValueError):
            return Response(
                {"error": "Collection not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        has_perm = request.user.is_superuser or request.user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), collection
        )
        if not has_perm:
            return Response(
                {"error": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )

        learners = (
            FacilityUser.objects.filter(memberships__collection=collection)
            .distinct()
            .order_by("full_name", "username")
        )

        total_sessions = AttendanceSession.objects.filter(collection=collection).count()
        user_attendance = self._get_user_attendance(
            collection, learners, total_sessions
        )
        user_quiz_stats = self._get_user_quiz_stats(collection, learners)
        user_cw_stats = self._get_user_cw_stats(collection, learners)
        user_last_activity = self._get_user_last_activity(collection, learners)
        user_interventions = self._get_user_interventions(collection, learners)

        active_assignments = Assignment.objects.filter(
            collection=collection, is_active=True
        )
        total_assignments = active_assignments.count()

        now = local_now()
        learner_results = []
        high_count = 0
        moderate_count = 0
        on_track_count = 0

        for l in learners:
            att = user_attendance.get(l.id, {"present": 0, "absent": 0, "rate": 100.0})
            q_stats = user_quiz_stats.get(l.id, {"total_quizzes": 0, "scores": []})
            cw = user_cw_stats.get(l.id, {"submitted_ids": set(), "grades": []})
            last_act = user_last_activity.get(l.id)

            factors, avg_quiz, missing_count = self._analyze_factors(
                att, total_sessions, q_stats, cw, total_assignments, last_act, now
            )

            risk_score = min(100, len(factors) * 35)
            if len(factors) >= 2:
                risk_level = "high"
                high_count += 1
            elif len(factors) == 1:
                risk_level = "moderate"
                moderate_count += 1
            else:
                risk_level = "low"
                on_track_count += 1

            itvs = user_interventions.get(l.id, [])
            active_itvs = [i for i in itvs if i["status"] in ("pending", "in_progress")]

            learner_results.append(
                {
                    "id": str(l.id),
                    "name": l.full_name or l.username,
                    "username": l.username,
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "risk_factors": factors,
                    "attendance_rate": att["rate"] if total_sessions > 0 else None,
                    "attendance_present": att["present"],
                    "attendance_total": total_sessions,
                    "quiz_average": avg_quiz,
                    "missing_assignments": (
                        missing_count if total_assignments > 0 else 0
                    ),
                    "total_assignments": total_assignments,
                    "last_active": last_act,
                    "interventions": itvs,
                    "active_intervention_count": len(active_itvs),
                    "latest_intervention": itvs[0] if itvs else None,
                }
            )

        risk_priority = {"high": 0, "moderate": 1, "low": 2}
        learner_results.sort(
            key=lambda x: (risk_priority[x["risk_level"]], x["name"].lower())
        )

        return Response(
            {
                "total_learners": len(learners),
                "high_risk_count": high_count,
                "moderate_risk_count": moderate_count,
                "on_track_count": on_track_count,
                "total_sessions": total_sessions,
                "total_assignments": total_assignments,
                "learners": learner_results,
            }
        )
