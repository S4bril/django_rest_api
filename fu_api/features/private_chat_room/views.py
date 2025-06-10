from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from fu_api.features.private_chat_room.serializers import (
    PrivateChatRoomSerializer,
)
from fu_api.features.private_chat_room.services import PrivateChatRoomService
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.private_chat_room_model import PrivateChatRoom


class ChatRoomCreateView(CreateAPIView):
    serializer_class = PrivateChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        member = get_object_or_404(CustomUser, id=pk)

        try:
            chat_room = PrivateChatRoomService.create_private_chat(
                creator=request.user,
                member=member,
            )
        except ValidationError as exc:
            raise exc

        serialized = self.get_serializer(
            chat_room, context=self.get_serializer_context()
        )
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class ChatRoomListView(ListAPIView):
    serializer_class = PrivateChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = PrivateChatRoom.objects.filter(members=self.request.user)
        qs = qs.annotate(latest_msg_created_at=Max("messages__created_at"))
        qs = qs.order_by("latest_msg_created_at")

        return qs
