from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.notification_model import Notification


class NotificationPullTests(APITestCase):
    def setUp(self):
        self.user = create_test_user("user1")
        self.other_user = create_test_user("user2")

        self.client.force_authenticate(self.user)

        self.url = "/api/notifications/"

        self.notif = Notification.objects.create(
            user=self.user, type="message", message="Pierwsze powiadomienie"
        )

    def test_pull_no_new_notifications(self):
        after = self.notif.created_at + timedelta(days=1)
        last_check = after.isoformat()

        response = self.client.get(self.url, {"last_check": last_check})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["notifications"]), 0)

    def test_pull_with_new_notifications(self):
        before = self.notif.created_at - timedelta(days=1)
        last_check = before.isoformat()

        response = self.client.get(self.url, {"last_check": last_check})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("notifications", response.data)
        self.assertEqual(self.notif.id, response.data["notifications"][0]["id"])
