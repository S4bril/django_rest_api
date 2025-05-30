from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.like_model import Like
from fu_api.models.match_model import Match
from fu_api.models.notification_model import Notification


class TestUserLikeListCreateView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.client.force_authenticate(user=self.user1)
        self.url = "/api/suggested-friends/like/"

    def test_unathorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_yourself(self):
        response = self.client.post(
            self.url, {"receiver_id": self.user1.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("must be different", response.data["detail"])

    def test_create_like_success(self):
        response = self.client.post(
            self.url, {"receiver_id": self.user2.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Like.objects.filter(sender=self.user1, receiver=self.user2).exists()
        )

        notification = Notification.objects.filter(
            user=self.user2, sender=self.user1, type="like"
        )
        self.assertTrue(notification.exists())

    def test_create_match_on_mutual_like(self):
        Like.objects.create(sender=self.user2, receiver=self.user1)

        response = self.client.post(
            self.url, {"receiver_id": self.user2.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Match created!")

        self.assertTrue(
            Match.objects.filter(
                first_user__in=[self.user1, self.user2],
                second_user__in=[self.user1, self.user2],
            ).exists()
        )
        self.assertFalse(
            Like.objects.filter(sender=self.user2, receiver=self.user1).exists()
        )

        notification1 = Notification.objects.filter(
            user=self.user1, sender=self.user2, type="match"
        )
        notification2 = Notification.objects.filter(
            user=self.user2, sender=self.user1, type="match"
        )
        self.assertTrue(notification1.exists() and notification2.exists())

    def test_duplicate_like_error(self):
        Like.objects.create(sender=self.user1, receiver=self.user2)
        response = self.client.post(
            self.url, {"receiver_id": self.user2.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already liked", response.data["detail"])

    def test_ivalid_id(self):
        response = self.client.post(self.url, {"receiver_id": 1000}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
