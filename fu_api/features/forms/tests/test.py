from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from unittest.mock import patch, mock_open
import json

class TestFormRetrieveView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/form/"
    
    @override_settings(FORM_PATH="/fake/path/form.json")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"fields": ["name", "email"]}))
    def test_retrieve_form_success(self, mock_file, mock_exists):
        mock_exists.return_value = True

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"fields": ["name", "email"]})

        mock_exists.assert_called_once_with("/fake/path/form.json")
        mock_file.assert_called_once_with("/fake/path/form.json", "r", encoding="utf-8")

    @override_settings(FORM_PATH="/fake/missing.json")
    @patch("os.path.exists")
    def test_form_file_not_found(self, mock_exists):
        mock_exists.return_value = False

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"error": "Form file not found"})
        mock_exists.assert_called_once_with("/fake/missing.json")
