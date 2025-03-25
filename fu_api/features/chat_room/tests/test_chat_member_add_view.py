from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.notification_model import Notification

class TestChatMemberAddView(APITestCase):
    def setUp(self):
        self.request_user = create_test_user("requester")
        self.target_user = create_test_user("target")
        self.other_user = create_test_user("other")

        self.group_chat = ChatRoom.objects.create(
            name="Test Room", 
            is_group=True
        )
        self.group_chat.members.add(self.request_user)

        self.private_chat = ChatRoom.objects.create(
            name="Private Room",
            is_group=False
        )
        self.private_chat.members.add(self.request_user, self.other_user)

        self.client.force_authenticate(user=self.request_user)

    def get_url(self, chat_room_id, user_id):
        return f"/api/chats/{chat_room_id}/members/{user_id}/add/"

    def test_unauthorized_access(self):
        self.client.logout()
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_to_private_chat_room(self):
        url = self.get_url(self.private_chat.id, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_not_in_chat_room(self):
        new_chat = ChatRoom.objects.create(name="New Room", is_group=True)
        new_chat.members.add(self.other_user)
        url = self.get_url(new_chat.id, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_target_user_blocks_requester(self):
        self.target_user.blocked_users.add(self.request_user)
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "You are blocked by target.")

    # def test_requester_blocks_target_user(self):
    #     self.request_user.blocked_users.add(self.target_user)
    #     url = self.get_url(self.group_chat.id, self.target_user.id)
    #     response = self.client.post(url)

    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(response.data["error"], "You have blocked target. Unblock to add them.")

    def test_user_already_in_chat(self):
        self.group_chat.members.add(self.target_user)
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "User is already in the chat.")

    def test_successful_member_addition(self):
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Member added successfully.")

        self.assertTrue(self.group_chat.members.filter(id=self.target_user.id).exists())

        notification = Notification.objects.filter(
            user=self.target_user,
            sender=self.request_user,
            type="chat_invite"
        ).first()
        self.assertIsNotNone(notification)
        self.assertIn(self.group_chat.name, notification.message)

    def test_invalid_chat_room_id(self):
        url = self.get_url(999, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_user_id(self):
        url = self.get_url(self.group_chat.id, 999)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
