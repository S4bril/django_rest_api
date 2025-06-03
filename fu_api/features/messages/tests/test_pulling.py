from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.message_model import Message


class PullingTests(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")

        self.chat = ChatRoom.objects.create(name="Private Chat", is_group=False)
        self.chat.members.add(self.user1, self.user2)

        self.first_msg = Message.objects.create(
            sender=self.user1, chat_room=self.chat, content="first"
        )
        self.second_msg = Message.objects.create(
            sender=self.user2, chat_room=self.chat, content="second"
        )

        self.client.force_authenticate(self.user1)
        self.url = f"/api/chats/{self.chat.id}/messages/"

    def test_pull_no_new_messages(self):
        last_check = self.second_msg.created_at.isoformat()
        response = self.client.get(self.url, {"last_check": last_check})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("has_new", response.data)
        self.assertFalse(response.data["has_new"])
        self.assertNotIn("messages", response.data)

    def test_pull_with_new_messages(self):
        last_check = self.first_msg.created_at.isoformat()

        new_msg = Message.objects.create(
            sender=self.user1, chat_room=self.chat, content="new"
        )

        response = self.client.get(self.url, {"last_check": last_check})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("has_new", response.data)
        self.assertTrue(response.data["has_new"])

        self.assertIn("messages", response.data)
        returned_ids = {msg_data["id"] for msg_data in response.data["messages"]}
        self.assertEqual(returned_ids, {new_msg.id})
