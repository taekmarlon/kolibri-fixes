from django.urls import include
from django.urls import re_path
from rest_framework import routers

from kolibri.core.chat.viewsets import ChatContactsView
from kolibri.core.chat.viewsets import ChatSyncView
from kolibri.core.chat.viewsets import ChatTypingView
from kolibri.core.chat.viewsets import ConversationViewSet
from kolibri.core.chat.viewsets import MessageViewSet

router = routers.SimpleRouter()
router.register(r"conversations", ConversationViewSet, basename="chat_conversations")
router.register(r"messages", MessageViewSet, basename="chat_messages")

urlpatterns = [
    re_path(r"^updates/$", ChatSyncView.as_view(), name="chat_updates"),
    re_path(r"^typing/$", ChatTypingView.as_view(), name="chat_typing"),
    re_path(r"^contacts/$", ChatContactsView.as_view(), name="chat_contacts"),
    re_path(r"^", include(router.urls)),
]
