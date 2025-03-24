from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.models.chat_room_model import ChatRoom
from fu_api.features.chat_room.serializers import ChatRoomSerializer
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.notification_model import Notification


class ChatRoomListCreateView(ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class ChatRoomMembersView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        chat_room = get_object_or_404(ChatRoom, pk=chat_room_id, members=self.request.user)

        return chat_room.members.all()


class ChatMemberAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id, pk):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)
        target_user = get_object_or_404(CustomUser, id=pk)

        if request.user in target_user.blocked_users.all():
            return Response({"error": f"You are blocked by {target_user.username}."}, status=status.HTTP_403_FORBIDDEN)

        if target_user in request.user.blocked_users.all():
            return Response({"error": f"You have blocked {target_user.username}. Unblock to add them."}, status=status.HTTP_400_BAD_REQUEST)

        if target_user in chat_room.members.all():
            return Response({"error": "User is already in the chat."}, status=status.HTTP_400_BAD_REQUEST)

        chat_room.members.add(target_user)

        Notification.objects.create(
            user=target_user,
            sender=request.user,
            type="chat_invite",
            message=f"You have been added to the chat: {chat_room.name}."
        )

        return Response({"message": "Member added successfully."}, status=status.HTTP_200_OK)


class ChatMemberRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id, pk):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)
        target_user = get_object_or_404(CustomUser, id=pk)

        if target_user not in chat_room.members.all():
            return Response({"error": "User is not in this chat."}, status=status.HTTP_400_BAD_REQUEST)

        chat_room.members.remove(target_user)
        return Response({"message": "Member removed successfully."}, status=status.HTTP_200_OK)


class LeaveChatRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)

        chat_room.members.remove(request.user)

        if chat_room.members.count() == 0:
            chat_room.delete()
            return Response({"message": "You were the last member. The chat room has been deleted."}, status=status.HTTP_200_OK)

        return Response({"message": "You have left the chat."}, status=status.HTTP_200_OK)
