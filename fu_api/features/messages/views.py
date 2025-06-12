from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from fu_api.features.common.services.new_since_filter_service import (
    NewSinceFilterService,
)
from fu_api.features.messages.serializers import MessageSerializer
from fu_api.features.messages.services import MessageService
from fu_api.models.message_model import Message
from fu_api.models.private_chat_room_model import PrivateChatRoom


class MessageListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_room = get_object_or_404(
            PrivateChatRoom,
            id=self.kwargs["chat_room_id"],
            members=self.request.user,
        )
        return Message.objects.filter(chat_room=chat_room)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if request.query_params.get("last_check"):
            queryset = queryset.exclude(sender=request.user)

        result = NewSinceFilterService.filter(request, queryset)

        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)

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


class MarkMessageAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        message.is_read = True
        message.save()
        return Response({'detail': 'Message marked as read.'}, status=status.HTTP_200_OK)
