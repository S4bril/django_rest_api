from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from fu_api.features.chat_room.services import ChatRoomService
from fu_api.models.chat_room_model import ChatRoom
from fu_api.features.chat_room.serializers import ChatRoomMemberSerializer, ChatRoomSerializer
from fu_api.models.custom_user_model import CustomUser


class ChatRoomListCreateView(ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        self.chat_room = ChatRoomService.create_chat(
            creator=self.request.user,
            name=validated_data["name"],
            is_group=validated_data["is_group"],
            member_ids=validated_data["members"]
        )


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

        try:
            ChatRoomService.add_member(chat_room, request.user, target_user)
            return Response({"message": f"{target_user.username} został dodany"}, status=status.HTTP_200_OK)

        except ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)


class ChatMemberRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id, pk):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)
        target_user = get_object_or_404(CustomUser, id=pk)

        try:
            ChatRoomService.remove_member(chat_room, request.user, target_user)
            return Response({"message": f"{target_user.username} został usunięty."}, status=status.HTTP_200_OK)

        except ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)


class PromoteToAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id, pk):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)
        target_user = get_object_or_404(CustomUser, id=pk)

        try:
            ChatRoomService.promote_member(chat_room, request.user, target_user)
            return Response({"message": f"{target_user.username} został administratorem"}, status=status.HTTP_200_OK)

        except ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)


class LeaveChatRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_group=True, members=request.user)

        try:
            ChatRoomService.leave_chat(chat_room, request.user)
            return Response({"message": "Opuściłeś czat."}, status=status.HTTP_200_OK)

        except ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
