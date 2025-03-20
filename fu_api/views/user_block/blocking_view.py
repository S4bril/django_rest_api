from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from fu_api.models.custom_user_model import CustomUser


class BlockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        user_to_block = get_object_or_404(CustomUser, id=user_id)

        if request.user == user_to_block:
            return Response({"error": "You cannot block yourself."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.blocked_users.add(user_to_block)
        return Response({"message": f"User {user_to_block.username} has been blocked."}, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        user_to_unblock = get_object_or_404(CustomUser, id=user_id)

        if user_to_unblock not in request.user.blocked_users.all():
            return Response({"error": "This user is not blocked."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.blocked_users.remove(user_to_unblock)
        return Response({"message": f"User {user_to_unblock.username} has been unblocked."}, status=status.HTTP_200_OK)
