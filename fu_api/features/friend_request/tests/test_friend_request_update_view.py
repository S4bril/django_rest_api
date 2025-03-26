from rest_framework.test import APITestCase
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.notification_model import Notification


class TestFriendRequestUpdateView(APITestCase):
    def setUp(self):
        self.sender = create_test_user(username="sender")
        self.receiver = create_test_user(username="receiver")
        self.other_user = create_test_user(username="other")

        self.pending_request = FriendRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            status="pending"
        )
        self.accepted_request = FriendRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            status="accepted"
        )

        self.client.force_authenticate(user=self.receiver)
        self.url = f"/api/friend-requests/{self.pending_request.id}/"

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.patch(self.url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_receiver_cannot_update(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_status_update(self):
        response = self.client.patch(self.url, {"status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Status must be either", response.data[0])

    def test_cannot_update_non_pending_request(self):
        url = f"/api/friend-requests/{self.accepted_request.id}/" 
        response = self.client.patch(url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_accept_request(self):
        response = self.client.patch(self.url, {"status": "accepted"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "accepted")
        self.assertIn(self.sender, self.receiver.friends.all())
        self.assertIn(self.receiver, self.sender.friends.all())

        notification = Notification.objects.filter(user=self.sender).first()
        self.assertIsNotNone(notification)
        self.assertIn("accepted", notification.message)

    def test_reject_request(self):
        response = self.client.patch(self.url, {"status": "rejected"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "rejected")

        self.assertNotIn(self.sender, self.receiver.friends.all())

        notification = Notification.objects.filter(user=self.sender).first()
        self.assertIsNotNone(notification)
        self.assertIn("rejected", notification.message)

    def test_cannot_modify_sender(self):
        response = self.client.patch(self.url, {"sender": self.other_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FriendRequest.objects.get(pk=self.pending_request.pk).sender, self.sender)

    def test_cannot_modify_receiver(self):
        response = self.client.patch(self.url, {"receiver": self.other_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FriendRequest.objects.get(pk=self.pending_request.pk).receiver, self.receiver)

    def test_invalid_request_id(self):
        url = "/api/friend-requests/1000/"
        response = self.client.patch(url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_sender_cannot_update(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.patch(self.url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
