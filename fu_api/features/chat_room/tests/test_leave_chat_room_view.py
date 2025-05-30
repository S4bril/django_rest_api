from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom


class TestLeaveChatRoomView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")

        self.group_chat = ChatRoom.objects.create(name="Test Group", is_group=True)
        self.group_chat.members.add(self.user1)

        self.private_chat = ChatRoom.objects.create(name="Private Chat", is_group=False)
        self.private_chat.members.add(self.user1)

        self.client.force_authenticate(user=self.user1)

    def get_url(self, chat_room_id):
        return f"/api/chats/{chat_room_id}/leave/"

    def test_unauthorized_access(self):
        self.client.logout()
        url = self.get_url(self.group_chat.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_leave_private_chat_room(self):
        url = self.get_url(self.private_chat.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_not_in_chat_room(self):
        new_group = ChatRoom.objects.create(name="New Room", is_group=True)
        new_group.members.add(self.user2)
        url = self.get_url(new_group.id)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_leave_with_remaining_members(self):
        self.group_chat.members.add(self.user2)
        self.group_chat.admins.add(self.user2)

        url = self.get_url(self.group_chat.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Opuściłeś czat.")

        self.assertNotIn(self.user1, self.group_chat.members.all())
        self.assertNotIn(self.user1, self.group_chat.admins.all())
        self.assertEqual(self.group_chat.members.count(), 1)

    def test_last_admin_leaving_assigns_new_admin(self):
        self.group_chat.members.add(self.user2)
        url = self.get_url(self.group_chat.id)

        response = self.client.post(url)
        updated_chat = ChatRoom.objects.get(id=self.group_chat.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(updated_chat.admins.count(), 1)
        self.assertEqual(updated_chat.admins.first(), self.user2)

    def test_last_member_leaving_deletes_chat(self):
        url = self.get_url(self.group_chat.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ChatRoom.objects.filter(id=self.group_chat.id).exists())

    def test_invalid_chat_room_id(self):
        url = self.get_url(1000)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
