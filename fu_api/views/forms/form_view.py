import json
import os
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class FormRetrieveView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        json_file_path = settings.FORM_PATH
        if not os.path.exists(json_file_path):
            return Response({"error": f"Form file not found"}, status=404)

        with open(json_file_path, "r", encoding="utf-8") as file:
            form_structure = json.load(file)
        return Response(form_structure, status=200)