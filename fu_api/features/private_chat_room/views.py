from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from fu_api.features.private_chat_room.serializers import (
    PrivateChatRoomSerializer,
)
from fu_api.features.private_chat_room.services import ChatRoomService
from fu_api.models.private_chat_room_model import PrivateChatRoom
from fu_api.models.custom_user_model import CustomUser


class ChatRoomListCreateView(ListCreateAPIView):
    serializer_class = PrivateChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = PrivateChatRoom.objects.filter(members=self.request.user)
        qs = qs.annotate(latest_msg_created_at=Max("messages__created_at"))
        qs = qs.order_by("-latest_msg_created_at")

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = get_object_or_404(CustomUser, id=validated_data["member_id"])

        try:
            validated_data = serializer.validated_data
            chat_room = ChatRoomService.create_private_chat(
                creator=self.request.user,
                member=member,
            )
            serializer.instance = chat_room
        except ValidationError as exc:
            raise exc

        serialized = PrivateChatRoomSerializer(chat_room, context=self.get_serializer_context())
        return Response(serialized.data, status=status.HTTP_201_CREATED)
