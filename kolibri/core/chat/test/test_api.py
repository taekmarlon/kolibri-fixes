from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.auth.models import Classroom
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.test.helpers import DUMMY_PASSWORD
from kolibri.core.auth.test.helpers import provision_device
from kolibri.core.chat.models import ChatConversation
from kolibri.core.chat.models import ChatMessage
from kolibri.core.chat.models import ChatParticipant
from kolibri.core.chat.models import ConversationKind
from kolibri.core.device.models import DevicePermissions
from kolibri.utils.time_utils import local_now


class ChatAPITestCase(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        provision_device()
        cls.facility = Facility.objects.create(name="Alpha Facility")
        cls.classroom = Classroom.objects.create(name="Class 1A", parent=cls.facility)

        cls.superadmin = FacilityUser.objects.create(
            username="superadmin", facility=cls.facility
        )
        cls.superadmin.set_password(DUMMY_PASSWORD)
        cls.superadmin.save()
        DevicePermissions.objects.create(user=cls.superadmin, is_superuser=True)

        cls.teacher = FacilityUser.objects.create(
            username="teacher", facility=cls.facility
        )
        cls.teacher.set_password(DUMMY_PASSWORD)
        cls.teacher.save()
        cls.classroom.add_coach(cls.teacher)

        cls.student1 = FacilityUser.objects.create(
            username="student1", facility=cls.facility
        )
        cls.student1.set_password(DUMMY_PASSWORD)
        cls.student1.save()
        cls.classroom.add_member(cls.student1)

        cls.student2 = FacilityUser.objects.create(
            username="student2", facility=cls.facility
        )
        cls.student2.set_password(DUMMY_PASSWORD)
        cls.student2.save()
        cls.classroom.add_member(cls.student2)

        # Another facility and stranger student
        cls.other_facility = Facility.objects.create(name="Beta Facility")
        cls.stranger = FacilityUser.objects.create(
            username="stranger", facility=cls.other_facility
        )
        cls.stranger.set_password(DUMMY_PASSWORD)
        cls.stranger.save()

    def test_teacher_can_message_enrolled_student(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("kolibri:core:chat_conversations-list")
        res = self.client.post(
            url,
            {"kind": ConversationKind.DIRECT, "recipient_id": str(self.student1.id)},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        conv_id = res.data["id"]

        # Send a message
        msg_url = reverse("kolibri:core:chat_messages-list")
        msg_res = self.client.post(
            msg_url,
            {"conversation_id": conv_id, "content": "Welcome to class!"},
            format="json",
        )
        self.assertEqual(msg_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(msg_res.data["content"], "Welcome to class!")

    def test_student_cannot_message_stranger_in_different_facility(self):
        self.client.force_authenticate(user=self.student1)
        url = reverse("kolibri:core:chat_conversations-list")
        res = self.client.post(
            url,
            {"kind": ConversationKind.DIRECT, "recipient_id": str(self.stranger.id)},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_superadmin_can_message_anyone(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse("kolibri:core:chat_conversations-list")
        res = self.client.post(
            url,
            {"kind": ConversationKind.DIRECT, "recipient_id": str(self.stranger.id)},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_message_lifecycle_send_edit_delete(self):
        # 1. Create conversation
        conv = ChatConversation.objects.create(
            kind=ConversationKind.DIRECT,
            facility=self.facility,
            created_by=self.student1,
        )
        ChatParticipant.objects.create(conversation=conv, user=self.student1)
        ChatParticipant.objects.create(conversation=conv, user=self.student2)

        self.client.force_authenticate(user=self.student1)
        # Send
        msg_url = reverse("kolibri:core:chat_messages-list")
        res = self.client.post(
            msg_url,
            {"conversation_id": str(conv.id), "content": "Original message"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        msg_id = res.data["id"]

        # Edit
        detail_url = reverse("kolibri:core:chat_messages-detail", kwargs={"pk": msg_id})
        edit_res = self.client.patch(
            detail_url, {"content": "Edited message"}, format="json"
        )
        self.assertEqual(edit_res.status_code, status.HTTP_200_OK)
        self.assertEqual(edit_res.data["content"], "Edited message")
        self.assertTrue(edit_res.data["is_edited"])

        # Reaction
        react_url = reverse("kolibri:core:chat_messages-react", kwargs={"pk": msg_id})
        react_res = self.client.post(react_url, {"emoji": "👍"}, format="json")
        self.assertEqual(react_res.status_code, status.HTTP_200_OK)
        self.assertEqual(react_res.data["action"], "added")

        # Delete for everyone
        del_res = self.client.delete(f"{detail_url}?for_everyone=true")
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertTrue(del_res.data["is_deleted"])
        self.assertEqual(del_res.data["content"], "🚫 This message was deleted")

    def test_cursor_pagination(self):
        conv = ChatConversation.objects.create(
            kind=ConversationKind.DIRECT,
            facility=self.facility,
            created_by=self.student1,
        )
        ChatParticipant.objects.create(conversation=conv, user=self.student1)
        ChatParticipant.objects.create(conversation=conv, user=self.student2)

        base_time = local_now() - timedelta(minutes=60)
        for i in range(30):
            ChatMessage.objects.create(
                conversation=conv,
                sender=self.student1,
                content=f"Message {i}",
                created_at=base_time + timedelta(seconds=i),
            )

        self.client.force_authenticate(user=self.student1)
        url = reverse("kolibri:core:chat_messages-list")
        res = self.client.get(f"{url}?conversation_id={conv.id}&limit=20")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["messages"]), 20)
        self.assertTrue(res.data["has_more"])
        cursor = res.data["cursor"]

        # Next page with cursor
        res_page2 = self.client.get(
            f"{url}?conversation_id={conv.id}&limit=20&before_id={cursor}"
        )
        self.assertEqual(res_page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_page2.data["messages"]), 10)
        self.assertFalse(res_page2.data["has_more"])
