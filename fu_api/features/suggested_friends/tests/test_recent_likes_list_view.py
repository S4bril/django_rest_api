from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.like_model import Like


class TestRecentLikesListView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")
        self.url = "/api/suggested-friends/recent-likes/"
        self.client.force_authenticate(user=self.user1)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_likes_are_sorted_by_created_at_descending(self):
        like1 = Like.objects.create(
            sender=self.user2, receiver=self.user1, created_at=timezone.now() - timedelta(days=2)
        )
        like2 = Like.objects.create(
            sender=self.user3, receiver=self.user1, created_at=timezone.now() - timedelta(days=1)
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        returned_sender_ids = [like["sender"]["id"] for like in response.data]

        self.assertEqual(returned_sender_ids, [like2.sender.id, like1.sender.id])

    def test_only_likes_received_by_user_are_returned(self):
        Like.objects.create(sender=self.user1, receiver=self.user2)
        Like.objects.create(sender=self.user2, receiver=self.user1)
        Like.objects.create(sender=self.user3, receiver=self.user1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        sender_ids = [like["sender"]["id"] for like in response.data]
        self.assertIn(self.user2.id, sender_ids)
        self.assertIn(self.user3.id, sender_ids)
        self.assertNotIn(self.user1.id, sender_ids)
