# from rest_framework.test import APITestCase
# from rest_framework import status
# from unittest.mock import patch

# from fu_api.features.common.tests.custom_user_factory import create_test_user


# class TestUserSuggestedFriendsRetrieveView(APITestCase):
#     def setUp(self):
#         self.user = create_test_user("user1")
#         self.client.force_authenticate(user=self.user)
#         self.url = '/api/suggested-friends/'

#     @patch('fu_api.features.suggested_friends.views.MatcherFactory')
#     def test_get_suggested_friends_default_method(self, mock_factory):
#         mock_matcher = mock_factory.get_matcher.return_value
#         mock_matcher.get_matches.return_value = [{'id': 2}, {'id': 3}]

#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('suggested_friends', response.data)
#         self.assertEqual(response.data['suggested_friends'], [{'id': 2}, {'id': 3}])
#         mock_factory.get_matcher.assert_called_with(method='knn')

#     @patch('fu_api.features.suggested_friends.views.MatcherFactory')
#     def test_get_suggested_friends_invalid_method(self, mock_factory):
#         mock_factory.get_matcher.side_effect = ValueError('Invalid method')
#         response = self.client.get(self.url + '?method=unknown')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], 'Invalid method')
