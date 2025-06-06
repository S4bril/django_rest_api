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

    def get_url(self, id):
        return f"/api/suggested-friends/like/{id}/"

    def test_unathorized_access(self):
        self.client.logout()
        url = self.get_url(self.user2.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_yourself(self):
        url = self.get_url(self.user1.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("must be different", response.data["detail"])

    def test_create_like_success(self):
        url = self.get_url(self.user2.id)
        response = self.client.post(url)

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
        url = self.get_url(self.user2.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Match created!")

        self.assertTrue(
            Match.objects.filter(
                user1__in=[self.user1, self.user2],
                user2__in=[self.user1, self.user2],
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
        url = self.get_url(self.user2.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already liked", response.data["detail"])

    def test_ivalid_id(self):
        url = self.get_url(1000)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
