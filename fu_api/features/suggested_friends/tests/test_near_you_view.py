from rest_framework.test import APITestCase
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.location_model import Location

class TestNearYouListView(APITestCase):
    def setUp(self):
        self.user = create_test_user("user0")
        self.user.location = Location.objects.create(latitude=0.0, longitude=0.0)
        self.user.save()    

        self.candidates = []
        for i in range(1, 15):
            u = create_test_user(f"user{i}")
            u.location = Location.objects.create(latitude=float(i), longitude=float(i))
            u.save()
            self.candidates.append(u)

        self.client.force_authenticate(user=self.user)
        self.url = "/api/suggested-friends/near-you/"

    def test_anauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nearby_order_and_limit(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 10)
        returned_usernames = [u["username"] for u in response.data]
        expected = [f"user{i}" for i in range(1, 11)]
        self.assertEqual(returned_usernames, expected)

    def test_no_location_returns_empty(self):
        self.user.location = None
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
