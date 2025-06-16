from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.message_model import Message
from fu_api.models.notification_model import Notification
from fu_api.models.private_chat_room_model import PrivateChatRoom


class MessageListCreateViewTests(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")

        self.chat = PrivateChatRoom.objects.create()
        self.chat.members.add(self.user1, self.user2)

        Message.objects.create(sender=self.user1, chat_room=self.chat, content="Hello")
        Message.objects.create(
            sender=self.user2, chat_room=self.chat, content="Hi there"
        )

        self.client.force_authenticate(self.user1)

        self.url = f"/api/private-chat/{self.chat.id}/messages/"

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_not_in_chat_gets_404(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_messages_authorized_member(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_successful_message_creation(self):
        data = {"content": "New message"}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 3)
        self.assertTrue(Notification.objects.filter(user=self.user2).exists())
        self.assertFalse(Notification.objects.filter(user=self.user1).exists())

    def test_create_message_non_member(self):
        non_member = create_test_user("non_member")
        self.client.force_authenticate(non_member)
        response = self.client.post(self.url, {"content": "Hi"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_message_when_blocked(self):
        self.user2.blocked_users.add(self.user1)
        response = self.client.post(self.url, {"content": "Blocked message"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("zablokowany przez", str(response.data["error_msg"]))

    def test_missing_content_field(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_serializer_data_structure(self):
        member_data = self.client.get(self.url).data[0]
        expected_fields = {"id", "created_at", "content", "sender_id", "is_read"}
        self.assertEqual(set(member_data.keys()), expected_fields)
