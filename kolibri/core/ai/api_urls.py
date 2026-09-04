from django.urls import re_path

from kolibri.core.ai.viewsets import AiChatView
from kolibri.core.ai.viewsets import AiGenerateActivityView
from kolibri.core.ai.viewsets import AiGenerateLessonView
from kolibri.core.ai.viewsets import AiGenerateQuizView
from kolibri.core.ai.viewsets import AiStatusView
from kolibri.core.ai.viewsets import AiTestConnectionView

urlpatterns = [
    re_path(r"^status/?$", AiStatusView.as_view(), name="ai_status"),
    re_path(r"^chat/?$", AiChatView.as_view(), name="ai_chat"),
    re_path(
        r"^generate_quiz/?$", AiGenerateQuizView.as_view(), name="ai_generate_quiz"
    ),
    re_path(
        r"^generate_activity/?$",
        AiGenerateActivityView.as_view(),
        name="ai_generate_activity",
    ),
    re_path(
        r"^generate_lesson/?$",
        AiGenerateLessonView.as_view(),
        name="ai_generate_lesson",
    ),
    re_path(
        r"^test_connection/?$",
        AiTestConnectionView.as_view(),
        name="ai_test_connection",
    ),
]
