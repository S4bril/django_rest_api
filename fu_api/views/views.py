import os
import json
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)

from fu_api.permissions import IsOwnerOrReadOnly
from ..models import CustomUser, Event
from ..serializers import (
    CustomUserSerializer,
    FriendSerializer,
    LocationSerializer,
    EventSerializer
)
from ..compute_suggested_friends.compute import get_suggested_friends


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


class EventsListCreateView(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EventsDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class EventLocationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs['pk'])

    def get_object(self):
        event = self.get_event()
        return event.location

    def update(self, request, *args, **kwargs):
        event = self.get_event()

        if event.location is None:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            location = serializer.save()
            event.location = location
            event.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return super().update(request, *args, **kwargs)

