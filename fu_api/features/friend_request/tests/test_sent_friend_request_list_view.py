from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.friend_request_model import FriendRequest


class TestSentFriendRequestListView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user(username="user1")
        self.user2 = create_test_user(username="user2")
        self.user3 = create_test_user(username="user3")

        self.sent_request1 = FriendRequest.objects.create(
            sender=self.user1, receiver=self.user2, status="pending"
        )
        self.sent_request2 = FriendRequest.objects.create(
            sender=self.user1, receiver=self.user3, status="pending"
        )
        FriendRequest.objects.create(
            sender=self.user2, receiver=self.user1, status="pending"
        )
        FriendRequest.objects.create(
            sender=self.user2, receiver=self.user3, status="pending"
        )

        self.client.force_authenticate(user=self.user1)
        self.url = "/api/friend-requests/sent/"

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_only_users_sent_requests(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        returned_ids = {req["id"] for req in response.data}
        self.assertIn(self.sent_request1.id, returned_ids)
        self.assertIn(self.sent_request2.id, returned_ids)

    def test_ordering_by_created_at_descending(self):
        self.sent_request1.created_at -= timedelta(hours=1)
        self.sent_request1.save()

        response = self.client.get(self.url)

        self.assertEqual(response.data[0]["id"], self.sent_request2.id)
        self.assertEqual(response.data[1]["id"], self.sent_request1.id)

    def test_empty_list_when_no_sent_requests(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_doesnt_show_received_requests(self):
        response = self.client.get(self.url)
        all_ids = [req["id"] for req in response.data]

        self.assertNotIn(
            FriendRequest.objects.get(sender=self.user2, receiver=self.user1).id,
            all_ids,
        )

    def test_serializer_data_structure(self):
        member_data = self.client.get(self.url).data[0]
        expected_fields = {"id", "sender", "receiver", "status", "created_at"}
        self.assertEqual(set(member_data.keys()), expected_fields)
