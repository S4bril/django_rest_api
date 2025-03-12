from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from fu_api.models import FriendRequest
from fu_api.serializers import FriendRequestSerializer

CustomUser = get_user_model()

class FriendRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver')
        receiver = CustomUser.objects.get(id=receiver_id)

        if receiver in request.user.friends.all():
            return Response({'detail': 'User is already your friend'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
            return Response({'detail': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(sender=request.user, receiver=receiver)

        # Notification.objects.create(
        #     user=receiver,
        #     sender=request.user,
        #     notification_type='friend_request',
        #     message=f"{request.user.username} sent you a friend request."
        # )

        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)


class SentFriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(sender=self.request.user).order_by('-created_at')


class FriendRequestAcceptView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request = FriendRequest.objects.get(id=self.kwargs['pk'], receiver=request.user, status='pending')
        friend_request.accept()

        # Notification.objects.create(
        #     user=friend_request.sender,
        #     sender=request.user,
        #     notification_type='friend_request',
        #     message=f"{request.user.username} accepted your friend request!"
        # )

        return Response({'detail': 'Friend request accepted'}, status=status.HTTP_200_OK)


class FriendRequestRejectView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request = FriendRequest.objects.get(id=self.kwargs['pk'], receiver=request.user, status='pending')
        friend_request.reject()

        return Response({'detail': 'Friend request rejected'}, status=status.HTTP_200_OK)
