from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

class MyAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_flow(self):
        # 1. Create a new user
        create_response = self.client.post(
            reverse('user-create'),
            {'username': 'testuser', 'password': 'testpass'}
        )
        self.assertEqual(create_response.status_code, 201)

        # 2. Log in to obtain a token (if using token authentication)
        login_response = self.client.post(
            reverse('login'),
            {'username': 'testuser', 'password': 'testpass'}
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.data.get('token')

        # 3. Use the token to access a protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        protected_response = self.client.get(reverse('protected-resource'))
        self.assertEqual(protected_response.status_code, 200)
