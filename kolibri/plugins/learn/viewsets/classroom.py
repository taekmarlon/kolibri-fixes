from django.db.models import Count
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import Sum
from django.db.models.fields import IntegerField
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from kolibri.core.api import ReadOnlyValuesViewset
from kolibri.core.auth.constants import role_kinds
from kolibri.core.auth.models import Classroom
from kolibri.core.content.models import ContentNode
from kolibri.core.courses.models import CourseSession
from kolibri.core.exams.models import Exam
from kolibri.core.exams.models import exam_assignment_lookup
from kolibri.core.lessons.models import Lesson
from kolibri.core.logger.models import AttemptLog
from kolibri.core.logger.models import MasteryLog

from . import _consolidate_courses_data
from . import _consolidate_lessons_data
from . import _map_contentnodes


class ExamProgressSerializer(serializers.Serializer):
    closed = serializers.BooleanField(allow_null=True)
    score = serializers.IntegerField(allow_null=True)
    answer_count = serializers.IntegerField(allow_null=True)
    started = serializers.BooleanField()


class ExamLearnerSerializer(serializers.Serializer):
    collection = serializers.CharField()
    active = serializers.BooleanField()
    archive = serializers.BooleanField()
    id = serializers.CharField()
    question_count = serializers.IntegerField()
    title = serializers.CharField()
    data_model_version = serializers.IntegerField()
    question_sources = serializers.ListField()
    instant_report_visibility = serializers.BooleanField(allow_null=True)
    progress = ExamProgressSerializer()
    missing_resource = serializers.BooleanField()


class LessonProgressSerializer(serializers.Serializer):
    resource_progress = serializers.FloatField()
    total_resources = serializers.IntegerField()


class LessonResourceSerializer(serializers.Serializer):
    content_id = serializers.CharField()
    channel_id = serializers.CharField()
    contentnode_id = serializers.CharField()
    progress = serializers.FloatField()
    contentnode = serializers.DictField(allow_null=True)


class LessonLearnerSerializer(serializers.Serializer):
    description = serializers.CharField(allow_blank=True)
    id = serializers.CharField()
    active = serializers.BooleanField()
    title = serializers.CharField()
    resources = LessonResourceSerializer(many=True, read_only=True)
    collection = serializers.CharField()
    progress = LessonProgressSerializer()
    missing_resource = serializers.BooleanField()


class CourseLearnerSerializer(serializers.Serializer):
    id = serializers.CharField()
    course_id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField()
    collection = serializers.CharField()
    unit_count = serializers.IntegerField()
    lesson_count = serializers.IntegerField()
    progress = serializers.FloatField()


class LearnerClassroomSerializer(serializers.ModelSerializer):
    exams = ExamLearnerSerializer(many=True, read_only=True)
    lessons = LessonLearnerSerializer(many=True, read_only=True)
    courses = CourseLearnerSerializer(many=True, read_only=True)

    class Meta:
        model = Classroom
        fields = ("id", "name", "exams", "lessons", "courses")


class LearnerClassroomViewset(ReadOnlyValuesViewset):
    """
    Returns all Classrooms for which the requesting User is a member,
    along with all associated assignments.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = LearnerClassroomSerializer
    deferred_fields = ("exams", "lessons", "courses")

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Classroom.objects.none()
        user = self.request.user
        if user.is_superuser:
            return Classroom.objects.all()
        coach_collections = user.roles.filter(
            kind__in=[role_kinds.ADMIN, role_kinds.COACH, role_kinds.ASSIGNABLE_COACH]
        ).values_list("collection_id", flat=True)
        return Classroom.objects.filter(
            Q(membership__user=user)
            | Q(id__in=coach_collections)
            | Q(parent__in=coach_collections)
        ).distinct()

    def consolidate(self, items, queryset):
        if not items:
            return items
        user = self.request.user
        item_classroom_ids = [c["id"] for c in items]

        if user.is_superuser:
            staff_classroom_ids = set(item_classroom_ids)
        else:
            coach_collections = user.roles.filter(
                kind__in=[
                    role_kinds.ADMIN,
                    role_kinds.COACH,
                    role_kinds.ASSIGNABLE_COACH,
                ]
            ).values_list("collection_id", flat=True)
            staff_classroom_ids = set(
                Classroom.objects.filter(id__in=item_classroom_ids)
                .filter(Q(id__in=coach_collections) | Q(parent__in=coach_collections))
                .values_list("id", flat=True)
            )

        lesson_filter = Q(
            collection__in=staff_classroom_ids,
            is_active=True,
        ) | Q(
            lesson_assignments__collection__membership__user=user,
            is_active=True,
            collection__in=item_classroom_ids,
        )

        lessons = (
            Lesson.objects.filter(lesson_filter)
            .distinct()
            .values(
                "description", "id", "is_active", "title", "resources", "collection"
            )
        )
        _consolidate_lessons_data(self.request, lessons)
        for lesson in lessons:
            lesson["active"] = lesson.pop("is_active")

        user_masterylog_content_ids = MasteryLog.objects.filter(user=user).values(
            "summarylog__content_id"
        )

        exam_filter = (
            Q(collection__in=staff_classroom_ids)
            | Q(
                assignments__collection__membership__user=user,
                collection__in=item_classroom_ids,
            )
        ) & (Q(active=True) | Q(id__in=user_masterylog_content_ids))

        exams = (
            Exam.objects.filter(exam_filter)
            .annotate(
                closed=Subquery(
                    MasteryLog.objects.filter(
                        summarylog__content_id=OuterRef("id"), user=user
                    ).values("complete")[:1]
                ),
                score=Subquery(
                    AttemptLog.objects.filter(
                        sessionlog__content_id=OuterRef("id"), user=user
                    )
                    .order_by()
                    .values_list("item")
                    .distinct()
                    .values("masterylog")
                    .annotate(total_correct=Sum("correct"))
                    .values("total_correct"),
                    output_field=IntegerField(),
                ),
                answer_count=Subquery(
                    AttemptLog.objects.filter(
                        sessionlog__content_id=OuterRef("id"), user=user
                    )
                    .order_by()
                    .values_list("item")
                    .distinct()
                    .values("masterylog")
                    .annotate(total_complete=Count("id"))
                    .values("total_complete"),
                    output_field=IntegerField(),
                ),
            )
            .distinct()
            .values(
                "collection",
                "active",
                "archive",
                "id",
                "question_count",
                "title",
                "closed",
                "answer_count",
                "data_model_version",
                "score",
                "question_sources",
                "instant_report_visibility",
            )
        )
        exam_node_ids = set()

        for exam in exams:
            exam_node_ids |= {
                exercise_id
                for exercise_id, _ in exam_assignment_lookup(
                    exam.get("question_sources", [])
                )
            }

        available_exam_ids = set(
            ContentNode.objects.filter_by_uuids(exam_node_ids).values_list(
                "id", flat=True
            )
        )

        contentnode_map = _map_contentnodes(self.request, available_exam_ids)

        for exam in exams:
            closed = exam.pop("closed")
            score = exam.pop("score")
            answer_count = exam.pop("answer_count")
            if closed is not None:
                exam["progress"] = {
                    "closed": closed,
                    "score": score,
                    "answer_count": answer_count,
                    "started": True,
                }
            else:
                exam["progress"] = {
                    "score": None,
                    "answer_count": None,
                    "closed": None,
                    "started": False,
                }
            missing_resource = False
            for exercise_id, _ in exam_assignment_lookup(
                exam.get("question_sources", [])
            ):
                if exercise_id not in contentnode_map:
                    missing_resource = True
                    break
            exam["missing_resource"] = missing_resource

        course_filter = Q(
            collection__in=staff_classroom_ids,
            is_active=True,
        ) | Q(
            assignments__collection__membership__user=user,
            collection__in=item_classroom_ids,
            is_active=True,
        )

        courses = (
            CourseSession.objects.filter(course_filter)
            .distinct()
            .values("id", "course", "title", "description", "is_active", "collection")
        )

        courses = _consolidate_courses_data(self.request, courses) if courses else []

        out_items = []
        for item in items:
            item["exams"] = [exam for exam in exams if exam["collection"] == item["id"]]
            item["lessons"] = [
                lesson for lesson in lessons if lesson["collection"] == item["id"]
            ]
            item["courses"] = [
                course for course in courses if course["collection"] == item["id"]
            ]
            out_items.append(item)
        return out_items
