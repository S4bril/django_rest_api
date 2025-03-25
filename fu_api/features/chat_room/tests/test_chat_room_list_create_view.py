from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom


class TestChatRoomListCreateView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")
        self.user4 = create_test_user("user4")

        self.user2.blocked_users.add(self.user1)

        self.client.force_authenticate(user=self.user1)

        self.url = "/api/chats/"

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authorized_user_member(self):
        chat_room_with_user = ChatRoom.objects.create(name="Room 1")
        chat_room_with_user.members.add(self.user1, self.user3)

        chat_room_without_user = ChatRoom.objects.create(name="Room 2")
        chat_room_without_user.members.add(self.user2, self.user4)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], chat_room_with_user.id)
        self.assertEqual(response.data[0]["name"], "Room 1")

    def test_create_private_chat_room_with_yourself(self):
        body = {
            "name": "Room",
            "members": [self.user1.id],
            "is_group": False
        }
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You cannot create private room with yourself.", response.data["members"][0])
        self.assertEqual(ChatRoom.objects.count(), 0)

    def test_create_private_chat_room_with_not_one_user(self):
        bodies = [
            {
                "name": "Room",
                "members": [],
                "is_group": False
            },
            {
                "name": "Room",
                "members": [self.user3.id, self.user4.id],
                "is_group": False
            }
        ]
        for body in bodies:
            response = self.client.post(self.url, body, format="json")
            self.assertIn("exactly one member", response.data["members"][0])

        self.assertEqual(ChatRoom.objects.count(), 0)

    def test_create_chat_room_when_blocked_by_user(self):
        body = {
            "name": "Room",
            "members": [self.user2.id],
            "is_group": True
        }
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ChatRoom.objects.count(), 0)

    def test_create_empty_chat_room(self):
        body = {
            "name": "Room",
            "members": [],
            "is_group": True
        }
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChatRoom.objects.count(), 1)
        chat_room = ChatRoom.objects.first()
        self.assertIn(self.user1, chat_room.members.all())

    def test_create_correct_chat_room(self):
        bodies = [
            {
                "name": "Room",
                "members": [self.user3.id],
                "is_group": False
            },
            {
                "name": "Room",
                "members": [self.user3.id, self.user4.id],
                "is_group": True
            }
        ]
        for body in bodies:
            response = self.client.post(self.url, body, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(ChatRoom.objects.count(), 2)

    def test_serializer_data_structure(self):
        chat_room = ChatRoom.objects.create(name="Room")
        chat_room.members.add(self.user1)
        member_data = self.client.get(self.url).data[0]
        expected_fields = {"id", "name", "is_group"}
        self.assertEqual(set(member_data.keys()), expected_fields)
