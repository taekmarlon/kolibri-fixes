import logging

from django.db.models import Q
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kolibri.core.api import ReadOnlyValuesViewset
from kolibri.core.auth.constants import role_kinds
from kolibri.core.lessons.models import Lesson
from kolibri.core.lessons.viewsets.lesson import ClassroomSerializer
from kolibri.core.logger.models import ContentSummaryLog
from kolibri.core.notifications.api import finish_lesson_resource
from kolibri.core.notifications.api import start_lesson_resource
from kolibri.utils.time_utils import local_now

from . import _consolidate_lessons_data

logger = logging.getLogger(__name__)


class LearnerLessonSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer(source="collection", read_only=True)
    active = serializers.BooleanField(source="is_active")
    progress = serializers.DictField(read_only=True)
    missing_resource = serializers.BooleanField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "description",
            "resources",
            "active",
            "collection",
            "classroom",
            "progress",
            "missing_resource",
        )


def _parse_float(value, default=0.0, min_val=None, max_val=None):
    try:
        val = float(value)
    except (ValueError, TypeError):
        val = default
    if min_val is not None:
        val = max(min_val, val)
    if max_val is not None:
        val = min(max_val, val)
    return val


def _save_custom_resource_log(user, resource, progress, time_spent, extra_fields):
    content_id = resource.get("content_id") or resource.get("contentnode_id")
    res_type = resource.get("resource_type", "")
    kind_map = {
        "youtube": "video",
        "video": "video",
        "image": "image",
        "html5": "html5",
        "h5p": "html5",
        "perseus": "exercise",
    }
    kind = kind_map.get(res_type, "document")
    now = local_now()

    log, created = ContentSummaryLog.objects.get_or_create(
        user=user,
        content_id=content_id,
        defaults={
            "start_timestamp": now,
            "end_timestamp": now,
            "progress": progress,
            "time_spent": time_spent,
            "kind": kind,
            "extra_fields": extra_fields if isinstance(extra_fields, dict) else {},
        },
    )
    if not created:
        log.end_timestamp = now
        if progress > log.progress:
            log.progress = progress
        if time_spent > 0:
            log.time_spent += time_spent
        if isinstance(extra_fields, dict):
            log.extra_fields.update(extra_fields)

    if log.progress >= 1.0 and not log.completion_timestamp:
        log.completion_timestamp = now
        log.progress = 1.0

    log.save()
    return log


class LearnerLessonViewset(ReadOnlyValuesViewset):
    """
    Special Viewset for Learners to view Lessons to which they are assigned.
    The core Lesson Viewset is locked down to Admin users only.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = LearnerLessonSerializer
    deferred_fields = ("progress", "missing_resource")

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Lesson.objects.none()
        user = self.request.user
        learner_lessons = Q(
            lesson_assignments__collection__membership__user=user,
            is_active=True,
        )
        if user.is_superuser:
            return Lesson.objects.all()
        coach_collections = user.roles.filter(
            kind__in=[role_kinds.ADMIN, role_kinds.COACH, role_kinds.ASSIGNABLE_COACH]
        ).values_list("collection_id", flat=True)
        return Lesson.objects.filter(
            learner_lessons
            | Q(collection__in=coach_collections)
            | Q(collection__parent__in=coach_collections)
        ).distinct()

    def consolidate(self, items, queryset):
        if not items:
            return items

        _consolidate_lessons_data(self.request, items)

        return items

    @action(
        detail=True,
        methods=["post"],
        url_path="update_custom_progress",
        url_name="update_custom_progress",
    )
    def update_custom_progress(self, request, pk=None):
        content_id = request.data.get("content_id")
        if not content_id:
            return Response(
                {"error": "content_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson = self.get_object()
        target_resource = next(
            (
                r
                for r in (lesson.resources or [])
                if content_id in (r.get("content_id"), r.get("contentnode_id"))
                and r.get("is_custom")
            ),
            None,
        )
        if not target_resource:
            return Response(
                {"error": "Custom resource not found in lesson"},
                status=status.HTTP_404_NOT_FOUND,
            )

        progress = _parse_float(request.data.get("progress"), 1.0, 0.0, 1.0)
        time_spent = _parse_float(request.data.get("time_spent"), 0.0, 0.0)
        extra_fields = request.data.get("extra_fields")

        log = _save_custom_resource_log(
            request.user, target_resource, progress, time_spent, extra_fields
        )

        node_id = target_resource.get("contentnode_id") or log.content_id
        try:
            start_lesson_resource(log, node_id, lesson_id=lesson.id)
            if log.progress >= 1.0:
                finish_lesson_resource(log, node_id, lesson_id=lesson.id)
        except Exception as e:
            logger.warning("Failed to emit lesson resource notification: %s", e)

        return Response(
            {
                "content_id": log.content_id,
                "progress": log.progress,
                "time_spent": log.time_spent,
            }
        )
