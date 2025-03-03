import os
import json
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from .models import CustomUser, Event, Location
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CustomUserSerializer,
    FriendSerializer,
    LocationSerializer,
    EventSerializer
)
from .compute_suggested_friends.compute import get_suggested_friends


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user


class UserCreateView(CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


class UserFriendsListView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_user(self, request):
        user = request.user
        user.delete()

        return Response(
            {"detail": "Your account has been deleted."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='get-profile')
    def get_profile(self, request):
        user = request.user
        serialized_user = CustomUserSerializer(user, context={'request': request})
        return Response(serialized_user.data)

    @action(detail=False, methods=['put'], url_path='update-profile')
    def update_profile(self, request):
        user = request.user

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='friends')
    def list_friends(self, request):
        user = request.user
        friends = user.friends.all()
        serialized_friends = FriendSerializer(friends, many=True, context={'request': request})
        return Response({"friends": serialized_friends.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='friends/remove/(?P<friend_id>[^/.]+)')
    def remove_friend(self, request, friend_id=None):
        user = request.user

        friend = get_object_or_404(CustomUser, id=friend_id)
        if friend not in user.friends.all():
            return Response({"error": "This user is not your friend."}, status=status.HTTP_400_BAD_REQUEST)

        if user not in friend.friends.all():
            return Response({"error": "You are not in this user's friends."}, status=status.HTTP_400_BAD_REQUEST)

        user.friends.remove(friend)
        friend.friends.remove(user)
        return Response({"message": f"User {friend.username} removed from friends."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='friends/add-friend/(?P<friend_id>[^/.]+)')
    def add_friend(self, request, friend_id=None):
        user = request.user

        friend = get_object_or_404(CustomUser, id=friend_id)
        if friend in user.friends.all():
            return Response({"error": "This user is already your friend."}, status=status.HTTP_400_BAD_REQUEST)

        user.friends.add(friend)
        return Response({"message": f"User {friend.username} added to your friends."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'], url_path='location')
    def update_location(self, request):
        user = request.user

        serializer = LocationSerializer(data=request.data)

        if serializer.is_valid():
            lat = serializer.validated_data['latitude']
            lon = serializer.validated_data['longitude']
            if user.location:
                user.location.latitude = lat
                user.location.longitude = lon
                user.location.save()
            else:
                new_location = Location.objects.create(
                    latitude=lat,
                    longitude=lon,
                )
                user.location = new_location
                user.save()

            return Response({"message": "Location updated successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='get-location')
    def get_location(self, request):
        user = request.user

        if user.location:
            serializer = LocationSerializer(user.location)
            return Response({"location": serializer.data}, status=status.HTTP_200_OK)

        return Response({"error": "Location not found for this user."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='suggested-friends')
    def get_suggested_friends(self, request):
        user = request.user
        suggested_friends = get_suggested_friends(user)
        serialized_suggested_friends = self.get_serializer(suggested_friends, many=True, context={'request': request})
        return Response({"suggested_friends": serialized_suggested_friends.data}, status=status.HTTP_200_OK)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user) | self.queryset.filter(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def all_events(self):
        return self.queryset


class GetFormView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        json_file_path = os.path.join(settings.BASE_DIR, "config", "json_forms", "form.json")

        if not os.path.exists(json_file_path):
            return Response({"error": "Form structure file not found"}, status=404)

        with open(json_file_path, "r", encoding="utf-8") as file:
            form_structure = json.load(file)
        return Response(form_structure, status=200)
