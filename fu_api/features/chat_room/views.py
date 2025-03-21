from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
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
        chat_room = get_object_or_404(ChatRoom, pk=chat_room_id)

        if self.request.user not in chat_room.members.all():
            raise PermissionDenied("You are not a member of this chat.")

        return chat_room.members.all()


class AddMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id):
        user_id = request.data.get("user_id")
        new_member = get_object_or_404(CustomUser, id=user_id)
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True)

        if request.user in new_member.blocked_users.all():
            return Response({"error": f"You are blocked by {new_member.username}"}, status=400)

        if new_member not in request.user.friends.all():
            return Response({"error": f"User with id: {user_id} is not your friend"}, status=400)

        if request.user not in chat_room.members.all():
            return Response({"error": "You are not in this group"}, status=403)

        if new_member in chat_room.members.all():
            return Response({"error": "User is already in the chat"}, status=400)

        chat_room.members.add(new_member)

        Notification.objects.create(
            user=new_member,
            sender=request.user,
            notification_type='chat_invite',
            message=f"You have been added to the chat: {chat_room.name}."
        )

        return Response({"message": "Member added successfully"}, status=200)


class RemoveMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id):
        user_id = request.data.get("user_id")
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True)
        member = get_object_or_404(CustomUser, id=user_id)

        if request.user not in chat_room.members.all():
            return Response({"error": "You are not a member of this chat"}, status=403)

        if member not in chat_room.members.all():
            return Response({"error": "User is not in this chat"}, status=400)

        chat_room.members.remove(member)

        Notification.objects.create(
            user=member,
            sender=request.user,
            notification_type='chat_invite',
            message=f"You have been removed from the chat: {chat_room.name}."
        )

        return Response({"message": "Member removed successfully"}, status=200)
