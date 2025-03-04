import os
import json
from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from .models import CustomUser, Event
from .serializers import (
    CustomUserSerializer,
    FriendSerializer,
    LocationSerializer,
    EventSerializer
)
from .compute_suggested_friends.compute import get_suggested_friends


class UsersListCreateView(ListCreateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]


class UsersRetrieveView(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserFriendsListView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()


class UserLocationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.location


class FormRetrieveView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        json_file_path = settings.FORM_PATH
        if not os.path.exists(json_file_path):
            return Response({"error": f"Form file not found"}, status=404)

        with open(json_file_path, "r", encoding="utf-8") as file:
            form_structure = json.load(file)
        return Response(form_structure, status=200)


class UserSuggestedFriendsRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suggested_friends = get_suggested_friends(request.user)
        serialized_suggested_friends = FriendSerializer(suggested_friends, many=True)
        return Response({"suggested_friends": serialized_suggested_friends.data}, status=HTTP_200_OK)


class EventViewSet(ModelViewSet):
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
