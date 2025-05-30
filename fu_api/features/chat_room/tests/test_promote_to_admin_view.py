from rest_framework.test import APITestCase
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.chat_room_model import ChatRoom

class TestPromoteToAdminView(APITestCase):
    def setUp(self):
        self.admin = create_test_user("admin")
        self.member = create_test_user("member")
        self.non_member = create_test_user("non_member")

        self.group_chat = ChatRoom.objects.create(
            name="Test Group",
            is_group=True
        )
        self.group_chat.members.add(self.admin, self.member)
        self.group_chat.admins.add(self.admin)

        self.client.force_authenticate(user=self.admin)
        self.url = f"/api/chats/{self.group_chat.id}/members/{self.member.id}/promote/"

    def get_url(self, chat_room_id, member_id):
        return f"/api/chats/{chat_room_id}/members/{member_id}/promote/"

    def test_non_admin_cannot_promote(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Tylko administrator może wykonać tę operację.", response.data["error_msg"])

    def test_promote_non_member(self):
        url = self.get_url(self.group_chat.id, self.non_member.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f"{self.non_member.username} nie należy do tego czatu.", response.data["error_msg"])

    def test_promote_existing_admin(self):
        self.group_chat.admins.add(self.member)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f"{self.member} już jest administratorem.", response.data["error_msg"])

    def test_successful_promotion(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.member, self.group_chat.admins.all())

    def test_invalid_chat_room(self):
        url = self.get_url(1000, self.member.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_user_id(self):
        url = self.get_url(self.group_chat.id, 1000)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
