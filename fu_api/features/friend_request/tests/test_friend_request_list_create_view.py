from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.notification_model import Notification


class TestFriendRequestListCreateView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")
        self.client.force_authenticate(user=self.user1)
        self.url = "/api/friend-requests/"

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_received_requests(self):
        FriendRequest.objects.create(sender=self.user2, receiver=self.user1)
        FriendRequest.objects.create(sender=self.user1, receiver=self.user2)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["sender"]["id"], self.user2.id)

    def test_list_ordered_by_created_at_descending(self):
        fr1 = FriendRequest.objects.create(sender=self.user2, receiver=self.user1)
        fr2 = FriendRequest.objects.create(sender=self.user3, receiver=self.user1)

        fr2.created_at = fr1.created_at - timedelta(hours=1)
        fr2.save()

        response = self.client.get(self.url)
        self.assertEqual(response.data[0]["id"], fr1.id)
        self.assertEqual(response.data[1]["id"], fr2.id)

    def test_create_request_to_yourself(self):
        response = self.client.post(self.url, {"receiver": self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Nie możesz wysłać zaproszenia do siebie", response.data["error_msg"]
        )

    def test_receiver_has_blocked_sender(self):
        self.user2.blocked_users.add(self.user1)
        response = self.client.post(self.url, {"receiver": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(f"Zostałeś zablokowany przez user2.", response.data["error_msg"])

    def test_receiver_already_friend(self):
        self.user1.friends.add(self.user2)
        response = self.client.post(self.url, {"receiver": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Jesteście już znajomymi.", response.data["error_msg"])

    def test_pending_request_exists(self):
        FriendRequest.objects.create(sender=self.user1, receiver=self.user2)
        response = self.client.post(self.url, {"receiver": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Zaproszenie już wysłane", response.data["error_msg"])

    def test_rejected_request_exists(self):
        FriendRequest.objects.create(
            sender=self.user1, receiver=self.user2, status="rejected"
        )
        response = self.client.post(self.url, {"receiver": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Twoje poprzednie zaproszenie zostało odrzucone.",
            response.data["error_msg"],
        )

    def test_successful_request_creation(self):
        response = self.client.post(self.url, {"receiver": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            FriendRequest.objects.filter(
                sender=self.user1, receiver=self.user2, status="pending"
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                sender=self.user1, user=self.user2, type="friend_request"
            ).exists()
        )

    def test_invalid_receiver_id(self):
        response = self.client.post(self.url, {"receiver": 1000})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_sender_automatically_set(self):
        _ = self.client.post(self.url, {"receiver": self.user2.id})
        friend_request = FriendRequest.objects.first()
        self.assertEqual(friend_request.sender, self.user1)
        self.assertEqual(friend_request.receiver, self.user2)

    def test_serializer_data_structure(self):
        FriendRequest.objects.create(sender=self.user2, receiver=self.user1)
        member_data = self.client.get(self.url).data[0]
        expected_fields = {"id", "sender", "receiver", "status", "created_at"}
        self.assertEqual(set(member_data.keys()), expected_fields)
