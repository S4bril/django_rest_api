from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user


class BlockUserViewTests(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")

        self.user1.blocked_users.add(self.user3)

        self.client.force_authenticate(self.user1)

    def get_url(self, user_id):
        return f"/api/users/{user_id}/block/"

    def test_unathorized_access(self):
        self.client.logout()
        url = self.get_url(self.user2.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_block_self(self):
        url = self.get_url(self.user1.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cannot block yourself", response.data["error"])
        self.assertFalse(self.user1.blocked_users.filter(id=self.user1.id).exists())

    def test_block_other_user(self):
        url = self.get_url(self.user2.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("has been blocked", response.data["message"])
        self.assertTrue(self.user1.blocked_users.filter(id=self.user2.id).exists())

    def test_block_already_blocked_user(self):
        initial_count = self.user1.blocked_users.filter(id=self.user3.id).count()
        self.assertEqual(initial_count, 1)

        url = self.get_url(self.user3.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        final_count = self.user1.blocked_users.filter(id=self.user3.id).count()
        self.assertEqual(final_count, 1)

    def test_block_nonexistent_user(self):
        url = self.get_url(1000)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unblock_user_unauthorized_access(self):
        self.client.logout()
        url = self.get_url(self.user3.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unblock_not_blocked_user(self):
        url = self.get_url(self.user2.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not blocked", response.data["error"])

    def test_unblock_success(self):
        url = self.get_url(self.user3.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("has been unblocked", response.data["message"])
        self.assertFalse(self.user1.blocked_users.filter(id=self.user3.id).exists())

    def test_unblock_nonexistent_user(self):
        url = self.get_url(1000)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unblock_other_users_blocked_user(self):
        self.client.force_authenticate(self.user2)
        url = self.get_url(self.user3.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not blocked", response.data["error"])
