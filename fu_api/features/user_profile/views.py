from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.features.common.serializers.location_serializer import LocationSerializer
from fu_api.features.user_profile.serializers import UserSerializer
from fu_api.models.custom_user_model import CustomUser


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserFriendsListView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()


class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        friend = get_object_or_404(CustomUser, pk=pk)

        if friend not in request.user.friends.all():
            return Response({'detail': 'User is not your friend'}, status=HTTP_400_BAD_REQUEST)

        request.user.friends.remove(friend)
        return Response({'detail': 'Friend removed successfully'}, status=HTTP_200_OK)


class UserLocationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.location

    def update(self, request, *args, **kwargs):
        user = self.request.user

        if user.location is None:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            location = serializer.save()
            user.location = location
            user.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return super().update(request, *args, **kwargs)
