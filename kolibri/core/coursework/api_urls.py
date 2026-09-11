from django.urls import include
from django.urls import re_path
from rest_framework import routers

from .viewsets import AnnouncementViewSet
from .viewsets import AssignmentSubmissionViewSet
from .viewsets import AssignmentViewSet
from .viewsets import AtRiskAnalyticsViewSet
from .viewsets import DiscussionReplyViewSet
from .viewsets import DiscussionThreadViewSet
from .viewsets import LearnerInterventionViewSet

router = routers.SimpleRouter()
router.register(r"announcement", AnnouncementViewSet, basename="announcement")
router.register(r"assignment", AssignmentViewSet, basename="assignment")
router.register(r"submission", AssignmentSubmissionViewSet, basename="submission")
router.register(
    r"discussionthread", DiscussionThreadViewSet, basename="discussionthread"
)
router.register(r"discussionreply", DiscussionReplyViewSet, basename="discussionreply")
router.register(
    r"learnerintervention", LearnerInterventionViewSet, basename="learnerintervention"
)
router.register(r"atriskanalytics", AtRiskAnalyticsViewSet, basename="atriskanalytics")

urlpatterns = [re_path(r"^", include(router.urls))]
