from django.urls import include
from django.urls import re_path
from rest_framework import routers

from .viewsets import AssignmentSubmissionViewSet
from .viewsets import AssignmentViewSet
from .viewsets import DiscussionReplyViewSet
from .viewsets import DiscussionThreadViewSet

router = routers.SimpleRouter()
router.register(r"assignment", AssignmentViewSet, basename="assignment")
router.register(r"submission", AssignmentSubmissionViewSet, basename="submission")
router.register(
    r"discussionthread", DiscussionThreadViewSet, basename="discussionthread"
)
router.register(r"discussionreply", DiscussionReplyViewSet, basename="discussionreply")

urlpatterns = [re_path(r"^", include(router.urls))]
