from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom


class TestChatMemberAddView(APITestCase):
    def setUp(self):
        self.admin_user = create_test_user("admin_user")
        self.non_admin_user = create_test_user("non_admin_user")
        self.target_user = create_test_user("target_user")
        self.other_user = create_test_user("other_user")

        self.group_chat = ChatRoom.objects.create(name="Test Group", is_group=True)
        self.group_chat.members.add(self.admin_user, self.non_admin_user)
        self.group_chat.admins.add(self.admin_user)

        self.private_chat = ChatRoom.objects.create(name="Private Chat", is_group=False)
        self.private_chat.members.add(self.admin_user, self.other_user)

        self.client.force_authenticate(user=self.admin_user)

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

    def test_user_already_in_chat(self):
        self.group_chat.members.add(self.target_user)
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            f"{self.target_user.username} już jest członkiem czatu.",
            response.data["error_msg"],
        )

    def test_non_admin_cannot_add_member(self):
        self.client.force_authenticate(user=self.non_admin_user)
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Tylko administrator może wykonać tę operację.", response.data["error_msg"]
        )

    def test_admin_can_add_member(self):
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.target_user, self.group_chat.members.all())

    def test_invalid_chat_room_id(self):
        url = self.get_url(1000, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_user_id(self):
        url = self.get_url(self.group_chat.id, 1000)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
