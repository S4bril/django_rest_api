from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from fu_api.features.suggested_friends.matchers.factory import MatcherFactory
from fu_api.models.custom_user_model import CustomUser


class UserSuggestedFriendsRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        method = request.query_params.get("method", "knn")
        try:
            matcher = MatcherFactory.get_matcher(method=method)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        suggested_friends = matcher.get_matches(request.user)
        return Response({"suggested_friends": suggested_friends}, status=status.HTTP_200_OK)


class UserRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        rejected_user = get_object_or_404(CustomUser, pk=pk)

        if request.user == rejected_user:
            return Response({"error": "You cannot reject yourself."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.rejected_users.add(rejected_user)
        return Response({"message": f"{rejected_user.username} added to rejected users"}, status=status.HTTP_200_OK)
