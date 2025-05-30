from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.message_model import Message
from fu_api.features.messages.serializers import MessageSerializer
from fu_api.features.messages.services import MessageService


class MessageListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            chat_room_id=self.kwargs["chat_room_id"]
        ).order_by("-timestamp")

    def create(self, request, *args, **kwargs):
        chat_room = get_object_or_404(
            ChatRoom, id=self.kwargs["chat_room_id"], members=request.user
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            msg = MessageService.send_message(
                sender=request.user,
                chat_room=chat_room,
                content=serializer.validated_data["content"]
            )
        except ValidationError as exc:
            raise exc

        serialized = MessageSerializer(msg, context={"request": request})
        return Response(serialized.data, status=status.HTTP_201_CREATED)
