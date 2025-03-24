from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView, ListAPIView, UpdateAPIView
from fu_api.models.friend_request_model import FriendRequest
from fu_api.features.friend_request.serializers import FriendRequestSerializer, FriendRequestUpdateSerializer


class FriendRequestListCreateView(ListCreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


class SentFriendRequestListView(ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(sender=self.request.user).order_by('-created_at')


class FriendRequestUpdateView(UpdateAPIView):
    serializer_class = FriendRequestUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            FriendRequest, 
            id=self.kwargs['pk'], 
            receiver=self.request.user, 
            status='pending'
        )
