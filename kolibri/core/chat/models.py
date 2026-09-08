import uuid

from django.db import models

from kolibri.core.auth.models import Collection
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.fields import DateTimeTzField
from kolibri.utils.time_utils import local_now


class ConversationKind:
    DIRECT = "direct"
    CLASSROOM = "classroom"
    BROADCAST = "broadcast"

    CHOICES = (
        (DIRECT, "Direct Message"),
        (CLASSROOM, "Classroom Chat"),
        (BROADCAST, "Global Broadcast"),
    )


class ChatConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(
        max_length=20,
        choices=ConversationKind.CHOICES,
        default=ConversationKind.DIRECT,
        db_index=True,
    )
    title = models.CharField(max_length=255, blank=True, default="")
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="facility_chat_conversations",
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="collection_chat_conversations",
    )
    created_by = models.ForeignKey(
        FacilityUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_conversations",
    )
    created_at = DateTimeTzField(default=local_now)
    updated_at = DateTimeTzField(default=local_now, db_index=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"ChatConversation({self.id}, {self.kind}, {self.title})"


class ChatParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    user = models.ForeignKey(
        FacilityUser,
        on_delete=models.CASCADE,
        related_name="chat_participations",
    )
    joined_at = DateTimeTzField(default=local_now)
    last_read_message_id = models.UUIDField(null=True, blank=True)
    last_read_at = DateTimeTzField(null=True, blank=True)
    is_muted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ("conversation", "user")

    def __str__(self):
        return f"ChatParticipant({self.user_id} in {self.conversation_id})"


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        FacilityUser,
        on_delete=models.CASCADE,
        related_name="sent_chat_messages",
    )
    content = models.TextField()
    created_at = DateTimeTzField(default=local_now, db_index=True)
    edited_at = DateTimeTzField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = DateTimeTzField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        FacilityUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_chat_messages",
    )
    hidden_for_users = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"ChatMessage({self.id} by {self.sender_id})"


class ChatMessageReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    user = models.ForeignKey(
        FacilityUser,
        on_delete=models.CASCADE,
        related_name="chat_reactions",
    )
    emoji = models.CharField(max_length=32)
    created_at = DateTimeTzField(default=local_now)

    class Meta:
        unique_together = ("message", "user", "emoji")

    def __str__(self):
        return f"Reaction({self.emoji} by {self.user_id} on {self.message_id})"


class ChatTypingStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="typing_statuses",
    )
    user = models.ForeignKey(
        FacilityUser,
        on_delete=models.CASCADE,
    )
    updated_at = DateTimeTzField(default=local_now)

    class Meta:
        unique_together = ("conversation", "user")
