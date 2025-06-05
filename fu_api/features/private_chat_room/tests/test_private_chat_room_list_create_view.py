from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.private_chat_room_model import PrivateChatRoom


class TestChatRoomListCreateView(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")
        self.user4 = create_test_user("user4")

        self.client.force_authenticate(user=self.user1)

        self.url = "/api/chats/"

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get(self):
        chat1 = PrivateChatRoom.objects.create()
        chat1.members.add(self.user1, self.user3)

        chat2 = PrivateChatRoom.objects.create()
        chat2.members.add(self.user2, self.user4)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], chat1.id)
        self.assertEqual(self.response.data[0]["member"]["id"], self.user3.id)

    def test_create_private_chat_room_with_yourself(self):
        body = {"member_id": self.user1.id}
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Nie możesz utworzyć chatu", response.data["error_msg"]
        )
        self.assertEqual(PrivateChatRoom.objects.count(), 0)

    def test_create_correct_chat_room(self):
        body = {"member_id": self.user3.id},
    
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(PrivateChatRoom.objects.count(), 1)

    def test_serializer_data_structure(self):
        chat_room = PrivateChatRoom.objects.create()
        chat_room.members.add(self.user1, self.user2)
        response = self.client.get(self.url).data[0]
        expected_fields = {"id", "name", "newest_message", "member"}
        self.assertEqual(set(response.keys()), expected_fields)
