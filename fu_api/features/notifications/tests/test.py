from rest_framework.test import APITestCase
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.notification_model import Notification


class NotificationViewTests(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")

        self.notification1 = Notification.objects.create(
            user=self.user1,
            sender=self.user2,
            type="message",
            message="Test message 1",
            is_read=False
        )

        self.notification2 = Notification.objects.create(
            user=self.user1,
            sender=self.user2,
            type="friend_request",
            message="Test message 2",
            is_read=True
        )

        self.other_user_notification = Notification.objects.create(
            user=self.user2,
            sender=self.user1,
            type="message",
            message="Other user message",
            is_read=False
        )

        self.client.force_authenticate(self.user1)

        self.url = "/api/notifications/"

    def get_read_url(self, notification_id):
        return self.url + f"{notification_id}/read/"

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_authorized(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        notification = response.data[0]
        self.assertIn("sender_username", notification)
        self.assertEqual(notification["sender_username"], "user2")

        all_ids = [response.data[0]["id"], response.data[1]["id"]]

        self.assertIn(self.notification1.id, all_ids)
        self.assertIn(self.notification2.id, all_ids)
        self.assertNotIn(self.other_user_notification.id, all_ids)

    def test_mark_read_unauthorized(self):
        self.client.logout()
        url = self.get_read_url(self.other_user_notification.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_read_success(self):
        url = self.get_read_url(self.notification1.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Notification marked as read")

        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_mark_read_other_users_notification(self):
        url = self.get_read_url(self.other_user_notification.id)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_non_existent_notification(self):
        url = self.get_read_url(1000)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_already_read_notification(self):
        url = self.get_read_url(self.notification2.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification2.refresh_from_db()
        self.assertTrue(self.notification2.is_read)
