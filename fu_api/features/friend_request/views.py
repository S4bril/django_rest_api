from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.custom_user_model import CustomUser
from fu_api.features.friend_request.serializers import (
    FriendRequestSerializer,
    FriendRequestCreateSerializer,
    FriendRequestUpdateSerializer
)
from fu_api.features.friend_request.services import FriendRequestService


class FriendRequestListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return FriendRequestCreateSerializer
        return FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receiver_id = serializer.validated_data["receiver"]
        receiver = get_object_or_404(CustomUser, pk=receiver_id)

        try:
            friend_req = FriendRequestService.send_request(request.user, receiver)
        except (ValidationError, PermissionDenied) as e:
            raise e

        output = FriendRequestSerializer(friend_req)
        return Response(output.data, status=status.HTTP_201_CREATED)


class SentFriendRequestListView(ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(sender=self.request.user).order_by('-created_at')


class FriendRequestUpdateView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestUpdateSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        fr = get_object_or_404(FriendRequest, pk=kwargs["pk"], receiver=request.user, status='pending')

        try:
            friend_req = FriendRequestService.respond_request(
                receiver=request.user,
                friend_req=fr,
                status=serializer.validated_data["status"]
            )
        except (ValidationError, PermissionDenied) as e:
            raise e

        serialized = FriendRequestSerializer(friend_req, context={"request": request})
        return Response(serialized.data, status=status.HTTP_200_OK)
