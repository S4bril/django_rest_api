from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime

from fu_api.features.common.tests.custom_user_factory import create_test_user

User = get_user_model()

class UsersListCreateViewTests(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.url = "/api/users/"

    def test_list_users_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        all_usernames = [data["username"] for data in response.data]
        self.assertIn("user1", all_usernames)
        self.assertIn("user2", all_usernames)

    def test_serialized_data_structure(self):
        response = self.client.get(self.url)
        user_data = next(u for u in response.data if u["username"] == "user1")

        self.assertIn("username", user_data)
        self.assertIn("sex", user_data)
        self.assertIn("bio", user_data)
        self.assertIn("image_url", user_data)
        self.assertIn("age", user_data)


class UsersRetrieveViewTests(APITestCase):
    def setUp(self):
        self.user = create_test_user("user")

    def get_url(self, user_id):
        return f"/api/users/{user_id}/"

    def test_retrieve_user_success(self):
        url = self.get_url(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user")
        self.assertEqual(response.data["sex"], "Mężczyzna")

    def test_retrieve_nonexistent_user(self):
        invalid_url = self.get_url(user_id=1000)
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
