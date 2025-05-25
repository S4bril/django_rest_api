# from rest_framework.test import APITestCase
# from rest_framework import status


# class UsersCreateViewTest(APITestCase):
#     def setUp(self):
#         self.url = "/api/users/"

#     def test_registration(self):
#         data = {
#             "email": "test@example.com",
#             "username": "user1",
#             "password": "securepassword123",
#             "birthday": "2002-01-01",
#             "sex_id": 0,
#             "bio": "I love writng unit tests.",
#             "passions": [1, 2, 3],
#             "profile_image": "iVBORw0KGgoAAAAN"
#         }

#         response = self.client.post(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         self.assertEqual(response.data["username"], "user1")
#         self.assertEqual(response.data["email"], "test@example.com")
#         self.assertIn("bio_embedding", response.data)
