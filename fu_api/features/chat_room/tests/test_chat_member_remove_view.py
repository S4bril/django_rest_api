from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom


class TestChatMemberRemoveView(APITestCase):
    def setUp(self):
        self.request_user = create_test_user("requester")
        self.target_user = create_test_user("target_user")
        self.other_user = create_test_user("other")

        self.group_chat = ChatRoom.objects.create(name="Test Group", is_group=True)
        self.group_chat.members.add(self.request_user)
        self.group_chat.admins.add(self.request_user)

        self.private_chat = ChatRoom.objects.create(name="Private Chat", is_group=False)
        self.private_chat.members.add(self.request_user, self.other_user)

        self.client.force_authenticate(user=self.request_user)

    def get_url(self, chat_room_id, user_id):
        return f"/api/chats/{chat_room_id}/members/{user_id}/remove/"

    def test_unauthorized_access(self):
        self.client.logout()
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_remove_from_private_room_chat(self):
        url = self.get_url(self.private_chat.id, self.other_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_not_in_chat_room(self):
        new_room = ChatRoom.objects.create(name="New Room", is_group=True)
        url = self.get_url(new_room.id, self.target_user.id)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_target_not_in_chat(self):
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            f"{self.target_user.username} nie należy do tego czatu.",
            response.data["error_msg"],
        )

    def test_successful_removal(self):
        self.group_chat.members.add(self.target_user)

        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], f"{self.target_user.username} został usunięty."
        )
        self.assertNotIn(self.target_user, self.group_chat.members.all())

    def test_invalid_chat_room_id(self):
        url = self.get_url(1000, self.target_user.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_user_id(self):
        url = self.get_url(self.group_chat.id, 1000)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_admin_cannot_remove_member(self):
        self.group_chat.members.add(self.target_user)
        self.group_chat.members.add(self.other_user)
        self.client.force_authenticate(user=self.other_user)

        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Tylko administrator może wykonać tę operację.", response.data["error_msg"]
        )

    def test_admin_can_remove_member(self):
        self.group_chat.members.add(self.target_user)
        url = self.get_url(self.group_chat.id, self.target_user.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.target_user, self.group_chat.members.all())
