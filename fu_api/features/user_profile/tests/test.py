from rest_framework import status
from rest_framework.test import APITestCase

from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.location_model import Location


class UserDetailViewTests(APITestCase):
    def setUp(self):
        self.user = create_test_user("user")
        self.url = "/api/me/"
        self.client.force_authenticate(self.user)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user")
        self.assertIn("image_url", response.data)
        self.assertIn("match_count", response.data)

    def test_update_user_profile(self):
        update_data = {"bio": "Updated bio", "password": "newpassword"}
        response = self.client.patch(self.url, update_data)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.bio, "Updated bio")
        self.assertTrue(self.user.check_password("newpassword"))

    def test_delete_user_account(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(username="testuser").exists())


class UserLocationDetailViewTests(APITestCase):
    def setUp(self):
        self.user = create_test_user("user")
        self.location = Location.objects.create(
            latitude=52.13,
            longitude=21.0,
        )
        self.user.location = self.location
        self.user.save()

        self.url = "/api/me/location/"
        self.client.force_authenticate(self.user)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_location(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_location(self):
        self.user.location = None
        self.user.save()

        new_location = {
            "latitude": 51.1,
            "longitude": 17.0333,
        }
        response = self.client.put(self.url, new_location)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.location.latitude, 51.1)
        self.assertEqual(self.user.location.longitude, 17.0333)

    def test_update_location(self):
        update_data = {
            "latitude": 51.01,
            "longitude": 16.46,
        }
        response = self.client.patch(self.url, update_data)
        self.location.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.location.latitude, 51.01)
        self.assertEqual(self.user.location.longitude, 16.46)

    def test_delete_location(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.location)
