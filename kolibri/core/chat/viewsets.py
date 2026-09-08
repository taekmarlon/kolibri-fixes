from collections import defaultdict
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kolibri.core.auth.models import Collection
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.chat.models import ChatConversation
from kolibri.core.chat.models import ChatMessage
from kolibri.core.chat.models import ChatMessageReaction
from kolibri.core.chat.models import ChatParticipant
from kolibri.core.chat.models import ChatTypingStatus
from kolibri.core.chat.models import ConversationKind
from kolibri.core.chat.permissions import can_access_conversation
from kolibri.core.chat.permissions import can_message_user
from kolibri.core.chat.permissions import get_eligible_contacts
from kolibri.core.chat.permissions import get_user_classrooms
from kolibri.core.chat.permissions import is_coach_or_admin
from kolibri.core.chat.permissions import is_superadmin
from kolibri.utils.time_utils import local_now


def serialize_user_brief(user):
    if not user:
        return None
    return {
        "id": str(user.id),
        "username": user.username,
        "full_name": getattr(user, "full_name", "") or user.username,
        "facility_name": getattr(getattr(user, "facility", None), "name", ""),
        "is_coach": is_coach_or_admin(user),
    }


def serialize_message(msg, user):
    is_hidden_for_user = str(user.id) in [str(u) for u in (msg.hidden_for_users or [])]
    if is_hidden_for_user:
        return None

    reactions_dict = defaultdict(
        lambda: {"count": 0, "users": [], "user_reacted": False}
    )
    for r in msg.reactions.all():
        reactions_dict[r.emoji]["count"] += 1
        reactions_dict[r.emoji]["users"].append(str(r.user_id))
        if r.user_id == user.id:
            reactions_dict[r.emoji]["user_reacted"] = True

    reactions_list = [
        {"emoji": emoji, "count": data["count"], "user_reacted": data["user_reacted"]}
        for emoji, data in reactions_dict.items()
    ]

    content = "🚫 This message was deleted" if msg.is_deleted else msg.content

    return {
        "id": str(msg.id),
        "conversation_id": str(msg.conversation_id),
        "sender": serialize_user_brief(msg.sender),
        "sender_id": str(msg.sender_id),
        "is_self": msg.sender_id == user.id,
        "content": content,
        "created_at": msg.created_at.isoformat(),
        "edited_at": msg.edited_at.isoformat() if msg.edited_at else None,
        "is_edited": msg.is_edited,
        "is_deleted": msg.is_deleted,
        "deleted_at": msg.deleted_at.isoformat() if msg.deleted_at else None,
        "reactions": reactions_list,
    }


class ConversationViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):  # noqa: C901
        user = request.user
        # 1. Direct conversations where user is a participant
        direct_conv_ids = set(
            ChatParticipant.objects.filter(user=user).values_list(
                "conversation_id", flat=True
            )
        )

        # 2. Classroom conversations for classrooms user belongs to
        user_classes = get_user_classrooms(user).values_list("id", flat=True)
        class_convs = ChatConversation.objects.filter(
            kind=ConversationKind.CLASSROOM, collection_id__in=user_classes
        )

        # Automatically ensure participant records exist for user in their classroom chats
        for cc in class_convs:
            ChatParticipant.objects.get_or_create(conversation=cc, user=user)
            direct_conv_ids.add(cc.id)

        # 3. Broadcast conversations
        broadcast_q = Q(kind=ConversationKind.BROADCAST)
        if not is_superadmin(user):
            broadcast_q &= Q(facility_id__isnull=True) | Q(facility_id=user.facility_id)
        broadcast_conv_ids = set(
            ChatConversation.objects.filter(broadcast_q).values_list("id", flat=True)
        )
        for bc_id in broadcast_conv_ids:
            ChatParticipant.objects.get_or_create(conversation_id=bc_id, user=user)
            direct_conv_ids.add(bc_id)

        all_convs = (
            ChatConversation.objects.filter(id__in=direct_conv_ids)
            .select_related("collection", "facility", "created_by")
            .prefetch_related("participants__user", "participants__user__facility")
            .order_by("-updated_at")
        )

        results = []
        for conv in all_convs:
            part = conv.participants.filter(user=user).first()
            last_read_at = part.last_read_at if part else None

            # Unread messages: messages in conversation, not sent by self, created after last_read_at
            unread_q = Q(conversation=conv) & ~Q(sender=user) & ~Q(is_deleted=True)
            if last_read_at:
                unread_q &= Q(created_at__gt=last_read_at)
            unread_count = ChatMessage.objects.filter(unread_q).count()

            user_id_str = str(user.id)
            recent_msgs = conv.messages.order_by("-created_at")[:10]
            last_msg = None
            for m in recent_msgs:
                if not (m.hidden_for_users and user_id_str in m.hidden_for_users):
                    last_msg = m
                    break

            # Determine title and avatar/participants
            title = conv.title
            other_participants = [
                p.user for p in conv.participants.all() if p.user_id != user.id
            ]
            if conv.kind == ConversationKind.DIRECT:
                if other_participants:
                    target = other_participants[0]
                    title = getattr(target, "full_name", "") or target.username
                else:
                    title = getattr(user, "full_name", "") or user.username + " (You)"
            elif conv.kind == ConversationKind.CLASSROOM:
                if not title and conv.collection:
                    title = conv.collection.name
            elif conv.kind == ConversationKind.BROADCAST:
                if not title:
                    title = "Global Announcement"

            # Determine facility name
            facility_name = ""
            if conv.facility:
                facility_name = conv.facility.name
            elif conv.collection and conv.collection.parent:
                facility_name = conv.collection.parent.name
            elif other_participants and getattr(
                other_participants[0], "facility", None
            ):
                facility_name = other_participants[0].facility.name
            elif getattr(conv.created_by, "facility", None):
                facility_name = conv.created_by.facility.name

            results.append(
                {
                    "id": str(conv.id),
                    "kind": conv.kind,
                    "title": title,
                    "facility_name": facility_name,
                    "facility_id": str(conv.facility_id) if conv.facility_id else None,
                    "collection_id": str(conv.collection_id)
                    if conv.collection_id
                    else None,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "unread_count": unread_count,
                    "participants": [
                        {
                            **serialize_user_brief(p.user),
                            "last_read_message_id": str(p.last_read_message_id)
                            if p.last_read_message_id
                            else None,
                        }
                        for p in conv.participants.all()
                    ],
                    "last_message": {
                        "id": str(last_msg.id) if last_msg else None,
                        "content": (
                            "🚫 Deleted message"
                            if last_msg.is_deleted
                            else last_msg.content
                        )
                        if last_msg
                        else None,
                        "sender_name": getattr(last_msg.sender, "full_name", "")
                        or last_msg.sender.username
                        if last_msg
                        else None,
                        "created_at": last_msg.created_at.isoformat()
                        if last_msg
                        else None,
                        "is_self": last_msg.sender_id == user.id if last_msg else False,
                    }
                    if last_msg
                    else None,
                }
            )

        return Response(results)

    def create(self, request):  # noqa: C901
        user = request.user
        data = request.data
        kind = data.get("kind", ConversationKind.DIRECT)

        if kind == ConversationKind.DIRECT:
            recipient_id = data.get("recipient_id")
            if not recipient_id:
                return Response(
                    {"error": "recipient_id is required for direct conversations"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            recipient = FacilityUser.objects.filter(id=recipient_id).first()
            if not recipient:
                return Response(
                    {"error": "Recipient user not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not can_message_user(user, recipient):
                return Response(
                    {"error": "You do not have permission to message this user."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if 1:1 conversation already exists between these 2 users
            existing_conv = (
                ChatConversation.objects.filter(kind=ConversationKind.DIRECT)
                .filter(participants__user=user)
                .filter(participants__user=recipient)
                .first()
            )
            if existing_conv:
                return Response(
                    {"id": str(existing_conv.id), "kind": existing_conv.kind}
                )

            # Create new direct conversation
            conv = ChatConversation.objects.create(
                kind=ConversationKind.DIRECT,
                facility=getattr(user, "facility", None)
                or getattr(recipient, "facility", None),
                created_by=user,
            )
            ChatParticipant.objects.create(conversation=conv, user=user)
            if recipient.id != user.id:
                ChatParticipant.objects.create(conversation=conv, user=recipient)

            return Response(
                {"id": str(conv.id), "kind": conv.kind},
                status=status.HTTP_201_CREATED,
            )

        elif kind == ConversationKind.CLASSROOM:
            collection_id = data.get("collection_id")
            collection = Collection.objects.filter(
                id=collection_id, kind="classroom"
            ).first()
            if not collection:
                return Response(
                    {"error": "Classroom not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # User must be enrolled or coach
            user_classes = get_user_classrooms(user).values_list("id", flat=True)
            if collection.id not in user_classes:
                return Response(
                    {"error": "You do not belong to this classroom."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            facility = None
            if hasattr(collection, "get_facility"):
                try:
                    facility = collection.get_facility()
                except Exception:
                    pass
            if not facility and collection.parent_id:
                facility = Facility.objects.filter(id=collection.parent_id).first()
            if not facility and getattr(user, "facility", None):
                facility = user.facility

            conv, created = ChatConversation.objects.get_or_create(
                kind=ConversationKind.CLASSROOM,
                collection=collection,
                defaults={
                    "title": collection.name,
                    "facility": facility,
                    "created_by": user,
                },
            )
            ChatParticipant.objects.get_or_create(conversation=conv, user=user)
            return Response(
                {"id": str(conv.id), "kind": conv.kind, "title": conv.title},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        elif kind == ConversationKind.BROADCAST:
            if not is_superadmin(user):
                return Response(
                    {"error": "Only superadmins can create global broadcasts."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            title = data.get("title", "Global Broadcast")
            facility_id = data.get("facility_id")
            conv = ChatConversation.objects.create(
                kind=ConversationKind.BROADCAST,
                title=title,
                facility_id=facility_id,
                created_by=user,
            )
            ChatParticipant.objects.create(conversation=conv, user=user)
            return Response(
                {"id": str(conv.id), "kind": conv.kind, "title": conv.title},
                status=status.HTTP_201_CREATED,
            )

        return Response({"error": "Invalid kind"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        user = request.user
        conv = ChatConversation.objects.filter(id=pk).first()
        if not conv or not can_access_conversation(user, conv):
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        part, _ = ChatParticipant.objects.get_or_create(conversation=conv, user=user)
        message_id = request.data.get("message_id")
        latest_msg = None
        if message_id:
            latest_msg = conv.messages.filter(id=message_id).first()
        if not latest_msg:
            latest_msg = conv.messages.order_by("-created_at").first()

        part.last_read_message_id = latest_msg.id if latest_msg else None
        part.last_read_at = local_now()
        part.save(update_fields=["last_read_message_id", "last_read_at"])
        return Response({"status": "ok", "last_read_at": part.last_read_at.isoformat()})


class MessageViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = request.user
        conversation_id = request.query_params.get("conversation_id")
        if not conversation_id:
            return Response(
                {"error": "conversation_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conv = ChatConversation.objects.filter(id=conversation_id).first()
        if not conv or not can_access_conversation(user, conv):
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        limit = min(int(request.query_params.get("limit", 25)), 50)
        before_id = request.query_params.get("before_id")

        q = Q(conversation=conv)
        if before_id:
            cursor_msg = ChatMessage.objects.filter(
                id=before_id, conversation=conv
            ).first()
            if cursor_msg:
                q &= Q(created_at__lt=cursor_msg.created_at) | Q(
                    created_at=cursor_msg.created_at, id__lt=cursor_msg.id
                )

        msgs = (
            ChatMessage.objects.filter(q)
            .select_related("sender", "sender__facility")
            .prefetch_related("reactions")
            .order_by("-created_at", "-id")[:limit]
        )

        serialized = []
        for m in reversed(msgs):
            item = serialize_message(m, user)
            if item:
                serialized.append(item)

        has_more = False
        if msgs:
            oldest_seen = msgs[len(msgs) - 1]
            has_more = ChatMessage.objects.filter(
                conversation=conv, created_at__lt=oldest_seen.created_at
            ).exists()

        return Response(
            {
                "messages": serialized,
                "has_more": has_more,
                "cursor": str(msgs[len(msgs) - 1].id) if (msgs and has_more) else None,
            }
        )

    def create(self, request):
        user = request.user
        conversation_id = request.data.get("conversation_id")
        content = str(request.data.get("content", "")).strip()

        if not conversation_id or not content:
            return Response(
                {"error": "conversation_id and content are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conv = ChatConversation.objects.filter(id=conversation_id).first()
        if not conv or not can_access_conversation(user, conv):
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        msg = ChatMessage.objects.create(
            conversation=conv,
            sender=user,
            content=content,
            created_at=local_now(),
        )

        # Update conversation updated_at
        conv.updated_at = msg.created_at
        conv.save(update_fields=["updated_at"])

        # Mark as read by sender
        part, _ = ChatParticipant.objects.get_or_create(conversation=conv, user=user)
        part.last_read_message_id = msg.id
        part.last_read_at = msg.created_at
        part.save(update_fields=["last_read_message_id", "last_read_at"])

        # Clear any typing status for sender
        ChatTypingStatus.objects.filter(conversation=conv, user=user).delete()

        return Response(serialize_message(msg, user), status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        user = request.user
        msg = ChatMessage.objects.filter(id=pk).first()
        if not msg:
            return Response(
                {"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if msg.sender_id != user.id:
            return Response(
                {"error": "You can only edit your own messages"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if msg.is_deleted:
            return Response(
                {"error": "Cannot edit a deleted message"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content = str(request.data.get("content", "")).strip()
        if not content:
            return Response(
                {"error": "Content cannot be blank"}, status=status.HTTP_400_BAD_REQUEST
            )

        msg.content = content
        msg.is_edited = True
        msg.edited_at = local_now()
        msg.save(update_fields=["content", "is_edited", "edited_at"])

        return Response(serialize_message(msg, user))

    def destroy(self, request, pk=None):
        user = request.user
        msg = ChatMessage.objects.filter(id=pk).first()
        if not msg:
            return Response(
                {"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND
            )

        for_everyone = (
            str(request.query_params.get("for_everyone", "false")).lower() == "true"
        )

        if for_everyone:
            # Can be deleted for everyone by author or by classroom coach/admin
            can_moderate = False
            if msg.sender_id == user.id or is_superadmin(user):
                can_moderate = True
            elif (
                msg.conversation.kind == ConversationKind.CLASSROOM
                and is_coach_or_admin(user)
            ):
                can_moderate = True

            if not can_moderate:
                return Response(
                    {
                        "error": "You do not have permission to delete this message for everyone"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            msg.is_deleted = True
            msg.deleted_at = local_now()
            msg.deleted_by = user
            msg.content = ""
            msg.save(
                update_fields=["is_deleted", "deleted_at", "deleted_by", "content"]
            )
            return Response(serialize_message(msg, user))
        else:
            # Delete for self
            hidden_list = list(msg.hidden_for_users or [])
            if str(user.id) not in hidden_list:
                hidden_list.append(str(user.id))
                msg.hidden_for_users = hidden_list
                msg.save(update_fields=["hidden_for_users"])
            return Response({"status": "deleted_for_self", "id": str(msg.id)})

    @action(detail=True, methods=["post"])
    def react(self, request, pk=None):
        user = request.user
        msg = ChatMessage.objects.filter(id=pk).first()
        if not msg or not can_access_conversation(user, msg.conversation):
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        emoji = str(request.data.get("emoji", "")).strip()
        if not emoji:
            return Response(
                {"error": "Emoji is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        existing = ChatMessageReaction.objects.filter(
            message=msg, user=user, emoji=emoji
        ).first()
        if existing:
            existing.delete()
            action_taken = "removed"
        else:
            ChatMessageReaction.objects.create(
                message=msg,
                user=user,
                emoji=emoji,
                created_at=local_now(),
            )
            action_taken = "added"

        return Response(
            {
                "action": action_taken,
                "message": serialize_message(msg, user),
            }
        )


class ChatSyncView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        since_str = request.query_params.get("since")
        now = local_now()

        # Parse timestamp or default to 15 seconds ago
        since = now - timedelta(seconds=15)
        if since_str:
            try:
                since = timezone.datetime.fromisoformat(
                    since_str.replace("Z", "+00:00")
                )
            except Exception:
                pass

        # Accessible conversations
        direct_conv_ids = set(
            ChatParticipant.objects.filter(user=user).values_list(
                "conversation_id", flat=True
            )
        )

        new_msgs = (
            ChatMessage.objects.filter(
                conversation_id__in=direct_conv_ids,
                created_at__gt=since,
            )
            .select_related("sender", "sender__facility")
            .prefetch_related("reactions")
            .order_by("created_at")
        )

        updated_msgs = (
            ChatMessage.objects.filter(
                conversation_id__in=direct_conv_ids,
                created_at__lte=since,
            )
            .filter(Q(edited_at__gt=since) | Q(deleted_at__gt=since))
            .select_related("sender", "sender__facility")
            .prefetch_related("reactions")
        )

        # Typing indicators (updated in the last 5 seconds)
        typing_cutoff = now - timedelta(seconds=5)
        active_typing = (
            ChatTypingStatus.objects.filter(
                conversation_id__in=direct_conv_ids,
                updated_at__gt=typing_cutoff,
            )
            .exclude(user=user)
            .select_related("user")
        )

        # Read receipts updated since `since`
        receipts = (
            ChatParticipant.objects.filter(
                conversation_id__in=direct_conv_ids,
                last_read_at__gt=since,
            )
            .exclude(user=user)
            .values(
                "conversation_id", "user_id", "last_read_message_id", "last_read_at"
            )
        )

        return Response(
            {
                "server_time": now.isoformat(),
                "new_messages": [
                    serialize_message(m, user)
                    for m in new_msgs
                    if serialize_message(m, user)
                ],
                "updated_messages": [
                    serialize_message(m, user)
                    for m in updated_msgs
                    if serialize_message(m, user)
                ],
                "typing": [
                    {
                        "conversation_id": str(t.conversation_id),
                        "user": serialize_user_brief(t.user),
                    }
                    for t in active_typing
                ],
                "read_receipts": [
                    {
                        "conversation_id": str(r["conversation_id"]),
                        "user_id": str(r["user_id"]),
                        "last_read_message_id": str(r["last_read_message_id"])
                        if r["last_read_message_id"]
                        else None,
                        "last_read_at": r["last_read_at"].isoformat()
                        if r["last_read_at"]
                        else None,
                    }
                    for r in receipts
                ],
            }
        )


class ChatTypingView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        conversation_id = request.data.get("conversation_id")
        is_typing = bool(request.data.get("is_typing", True))

        if not conversation_id:
            return Response(
                {"error": "conversation_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conv = ChatConversation.objects.filter(id=conversation_id).first()
        if not conv or not can_access_conversation(user, conv):
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        if is_typing:
            ChatTypingStatus.objects.update_or_create(
                conversation=conv,
                user=user,
                defaults={"updated_at": local_now()},
            )
        else:
            ChatTypingStatus.objects.filter(conversation=conv, user=user).delete()

        return Response({"status": "ok"})


class ChatContactsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        query = str(request.query_params.get("q", "")).strip()

        contacts = get_eligible_contacts(user)
        if query:
            contacts = contacts.filter(
                Q(username__icontains=query) | Q(full_name__icontains=query)
            )

        # Also get user's classrooms to offer class group chats
        user_classes = get_user_classrooms(user)
        if query:
            user_classes = user_classes.filter(name__icontains=query)

        return Response(
            {
                "contacts": [serialize_user_brief(c) for c in contacts[:50]],
                "classrooms": [
                    {
                        "id": str(c.id),
                        "name": c.name,
                        "kind": "classroom",
                        "facility_name": getattr(c.parent, "name", "")
                        if c.parent
                        else "",
                    }
                    for c in user_classes
                ],
            }
        )
