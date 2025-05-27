from rest_framework.test import APITestCase
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user

class TestUserRejectView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.client.force_authenticate(user=self.user1)
        self.url = f"/api/suggested-friends/reject/{self.user2.id}/"

    def test_list_anauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reject_other_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user2, self.user1.rejected_users.all())
        self.assertEqual(response.data["message"], f"{self.user2.username} added to rejected users")

    def test_reject_self_error(self):
        url_self = f"/api/suggested-friends/reject/{self.user1.id}/"
        response = self.client.post(url_self)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "You cannot reject yourself.")

    def test_ivalid_id(self):
        response = self.client.post(f"/api/suggested-friends/reject/{1000}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
