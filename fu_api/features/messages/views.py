from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from fu_api.features.common.services.new_since_filter_service import (
    NewSinceFilterService,
)
from fu_api.features.messages.serializers import MessageSerializer
from fu_api.features.messages.services import MessageService
from fu_api.models.private_chat_room_model import PrivateChatRoom
from fu_api.models.message_model import Message


class MessageListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_room = get_object_or_404(
            PrivateChatRoom,
            id=self.kwargs["chat_room_id"],
            members=self.request.user,
        )
        return Message.objects.filter(chat_room=chat_room).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("-created_at")
        result = NewSinceFilterService.filter(request, queryset)

        if result["error"]:
            return result["error"]

        if not result["has_new"]:
            return Response({"has_new": False})

        serializer = self.get_serializer(result["queryset"], many=True)
        return Response({"has_new": True, "messages": serializer.data})

    def create(self, request, *args, **kwargs):
        chat_room = get_object_or_404(
            PrivateChatRoom, id=self.kwargs["chat_room_id"], members=request.user
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            msg = MessageService.send_message(
                sender=request.user,
                chat_room=chat_room,
                content=serializer.validated_data["content"],
            )
        except ValidationError as exc:
            raise exc

        serialized = MessageSerializer(msg, context={"request": request})
        return Response(serialized.data, status=status.HTTP_201_CREATED)
