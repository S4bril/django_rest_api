from datetime import timedelta
from django.utils.timezone import now, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from fu_api.features.common.tests.custom_user_factory import create_test_user
from fu_api.models.match_model import Match

class TestMatchesListView(APITestCase):
    def setUp(self):
        self.user1 = create_test_user("user1")
        self.user2 = create_test_user("user2")
        self.user3 = create_test_user("user3")

        Match.objects.create(first_user=self.user1, second_user=self.user2, created_at=now() - timedelta(days=1))
        Match.objects.create(first_user=self.user3, second_user=self.user1, created_at=now())

        self.client.force_authenticate(user=self.user1)
        self.url = '/api/suggested-friends/matches/'

    def test_list_anauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_matches(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertIn('id', item)
            self.assertIn('created_at', item)
            self.assertIn('matched_user', item)

        created_dates = [item['created_at'] for item in data]
        self.assertEqual(created_dates, sorted(created_dates, reverse=True))
