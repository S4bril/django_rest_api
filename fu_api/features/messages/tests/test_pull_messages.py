from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.message_model import Message
from fu_api.models.private_chat_room_model import PrivateChatRoom


class TestPullMessages(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")

        self.chat = PrivateChatRoom.objects.create()
        self.chat.members.add(self.user1, self.user2)

        self.msg = Message.objects.create(
            sender=self.user1, chat_room=self.chat, content="first"
        )

        self.client.force_authenticate(self.user1)
        self.url = f"/api/private-chat/{self.chat.id}/messages/"

    def test_pull_no_new_messages(self):
        after = self.msg.created_at + timedelta(days=1)
        last_check = after.isoformat()
        response = self.client.get(self.url, {"last_check": last_check})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_pull_with_new_messages(self):
        before = self.msg.created_at - timedelta(days=1)
        last_check = before.isoformat()

        response = self.client.get(self.url, {"last_check": last_check})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.msg.id, response.data[0]["id"])
