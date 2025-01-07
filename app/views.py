import os
import json
import logging

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import viewsets, mixins, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from .models import CustomUser, Event, Location
from .permissions import IsOwnerOrReadOnly
from . import serializers


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]
    
    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['put'], url_path='update-profile')
    def update_profile(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='friends')
    def list_friends(self, request, pk=None):
        user = get_object_or_404(CustomUser, id=pk)
        friends = user.friends.all()
        serialized_friends = serializers.FriendSerializer(friends, many=True)
        return Response({"friends": serialized_friends.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='friends/remove/(?P<friend_id>[^/.]+)')
    def remove_friend(self, request, pk=None, friend_id=None):
        user = get_object_or_404(CustomUser, id=pk)
        if user != request.user:
            return Response({"error": "You can only manage your own friends."}, status=status.HTTP_403_FORBIDDEN)
        
        friend = get_object_or_404(CustomUser, id=friend_id)
        if friend not in user.friends.all():
            return Response({"error": "This user is not your friend."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user not in friend.friends.all():
            return Response({"error": "You are not in this user's friends."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.friends.remove(friend)
        friend.friends.remove(user)
        return Response({"message": f"User {friend.username} removed from friends."}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], url_path='friends/add-friend/(?P<friend_id>[^/.]+)')
    def add_friend(self, request, pk=None, friend_id=None):
        user = get_object_or_404(CustomUser, id=pk)
        if user != request.user:
            return Response({"error": "You can only manage your own friends."}, status=status.HTTP_403_FORBIDDEN)
        
        friend = get_object_or_404(CustomUser, id=friend_id)
        if friend in user.friends.all():
            return Response({"error": "This user is already your friend."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.friends.add(friend)
        friend.friends.add(user)
        return Response({"message": f"User {friend.username} added to your friends."}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['put'], url_path='location')
    def update_location(self, request, pk=None):
        user = get_object_or_404(CustomUser, id=pk)

        if user != request.user:
            return Response({"error": "You can only update your own location."}, status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.LocationSerializer(data=request.data)

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
        
    @action(detail=True, methods=['get'], url_path='get_location')
    def get_location(self, request, pk=None):
        user = get_object_or_404(CustomUser, id=pk)

        if user != request.user:
            return Response({"error": "You can only access your own location."}, status=status.HTTP_403_FORBIDDEN)

        if user.location:
            serializer = serializers.LocationSerializer(user.location)
            return Response({"location": serializer.data}, status=status.HTTP_200_OK)

        return Response({"error": "Location not found for this user."}, status=status.HTTP_404_NOT_FOUND)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = serializers.EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user) | self.queryset.filter(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def all_events(self):
        return self.queryset


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"detail": "Invalid credentials"}, status=401)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            user_id = token["user_id"]
            token.blacklist()

            return Response({"detail": f"{CustomUser.objects.get(id=user_id)} logged out successfully"})

        except Exception as e:
            return Response({"detail": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
class GetFormView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        json_file_path = os.path.join(settings.BASE_DIR, "app", "config", "form.json")
        print(json_file_path)
        
        if not os.path.exists(json_file_path):
            return Response({"error": "Form structure file not found"}, status=404)

        with open(json_file_path, "r", encoding="utf-8") as file:
            form_structure = json.load(file)
        return Response(form_structure, status=200)
