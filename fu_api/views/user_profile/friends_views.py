from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from fu_api.serializers.friend_serializers import FriendSerializer
from fu_api.models.custom_user_model import CustomUser


class UserFriendsListView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()


class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            friend = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Friend not found'}, status=HTTP_404_NOT_FOUND)

        if friend not in request.user.friends.all():
            return Response({'detail': 'User is not your friend'}, status=HTTP_400_BAD_REQUEST)

        request.user.friends.remove(friend)
        return Response({'detail': 'Friend removed successfully'}, status=HTTP_200_OK)