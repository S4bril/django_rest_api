from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from fu_api.models.chat_room_model import ChatRoom
from fu_api.features.chat_room.serializers import ChatRoomMemberSerializer, ChatRoomSerializer
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.notification_model import Notification


class ChatRoomListCreateView(ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user)


class ChatRoomMembersView(ListAPIView):
    serializer_class = ChatRoomMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_chat_room().members.all()

    def get_chat_room(self):
        chat_room_id = self.kwargs['chat_room_id']
        return get_object_or_404(ChatRoom, pk=chat_room_id, members=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['chat_room'] = self.get_chat_room()
        return context


class ChatMemberAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id, pk):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)
        target_user = get_object_or_404(CustomUser, id=pk)

        if not chat_room.admins.filter(id=request.user.id).exists():
            return Response(
                {"error": "Only admins can add members."},
                status=status.HTTP_403_FORBIDDEN
            )

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
            message=f"Dodano Cię do czatu: {chat_room.name}."
        )

        return Response({"message": "Member added successfully."}, status=status.HTTP_200_OK)


class ChatMemberRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id, pk):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)
        target_user = get_object_or_404(CustomUser, id=pk)

        if not chat_room.admins.filter(id=request.user.id).exists():
            return Response({"error": "Only admins can remove members."}, status=status.HTTP_403_FORBIDDEN)

        if target_user not in chat_room.members.all():
            return Response({"error": "User is not in this chat."}, status=status.HTTP_400_BAD_REQUEST)

        chat_room.members.remove(target_user)
        return Response({"message": "Member removed successfully."}, status=status.HTTP_200_OK)


class PromoteToAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id, pk):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, admins=request.user)
        target_user = get_object_or_404(CustomUser, id=pk)

        if target_user not in chat_room.members.all():
            return Response({"error": "User is not a member of this chat."}, status=400)
        
        if chat_room.admins.filter(id=target_user.id).exists():
            return Response({"error": "User is already an admin."}, status=400)
        
        chat_room.admins.add(target_user)
        return Response({"message": "User promoted to admin successfully."}, status=200)


class LeaveChatRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)

        chat_room.members.remove(request.user)
        chat_room.admins.remove(request.user)

        if chat_room.members.count() == 0:
            chat_room.delete()
            return Response({"message": "You were the last member. The chat room has been deleted."}, status=status.HTTP_200_OK)
        
        if chat_room.admins.count() == 0:
            new_admin = chat_room.members.order_by('id').first()
            chat_room.admins.add(new_admin)

        return Response({"message": "You have left the chat."}, status=status.HTTP_200_OK)
