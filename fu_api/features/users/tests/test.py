from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.models.custom_user_model import CustomUser


class UsersCreateViewTest(APITestCase):
    def setUp(self):
        self.url = "/api/users/"

    def test_registration(self):
        data = {
            "email": "test@example.com",
            "username": "user1",
            "password": "securepassword123",
            "birthday": "2002-01-01",
            "sex_id": 0,
            "bio": "I love writng unit tests.",
            "passions_ids": [1, 2, 3],
        }
        expected_response = {
            "email": "test@example.com",
            "username": "user1",
            "birthday": "2002-01-01",
            "bio": "I love writng unit tests.",
            "image_url": None,
            "passions": ["Piłka nożna", "Koszykówka", "Siatkówka"],
            "match_count": 0,
            "sex": "Mężczyzna",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for field in expected_response:
            self.assertEqual(expected_response[field], response.data[field])

        user = CustomUser.objects.get(email="test@example.com")
        self.assertTrue(hasattr(user, "bio_embedding"))
