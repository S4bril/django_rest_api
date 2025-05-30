from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom


class TestChatRoomMembersView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")
        self.user4 = create_test_user("user4")

        self.chat_room = ChatRoom.objects.create(name="Room")
        self.chat_room.members.add(self.user1, self.user2, self.user3, self.user4)

        self.url = f"/api/chats/{self.chat_room.id}/members/"

        self.client.force_authenticate(user=self.user1)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user_not_member(self):
        new_chat_room = ChatRoom.objects.create(name="New Room", is_group=False)
        new_chat_room.members.add(self.user2)

        response = self.client.get(f"/api/chats/{new_chat_room.id}/members/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_chat_room_does_not_exist(self):
        response = self.client.get("/api/chats/10000/members/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authorized_user_is_member(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        returned_usernames = {member["username"] for member in response.data}
        self.assertIn(self.user1.username, returned_usernames)
        self.assertIn(self.user2.username, returned_usernames)
        self.assertIn(self.user3.username, returned_usernames)
        self.assertIn(self.user4.username, returned_usernames)

    def test_serializer_data_structure(self):
        response = self.client.get(self.url)
        member_data = response.data[0]
        expected_fields = {"username", "image_url", "is_admin"}
        self.assertEqual(set(member_data.keys()), expected_fields)
