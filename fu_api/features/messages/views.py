from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.message_model import Message 
from fu_api.features.messages.serializers import MessageSerializer


class MessageListCreateView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        return get_object_or_404(Message, chat_room_id=chat_room_id)

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        chat_room = get_object_or_404(ChatRoom, id=self.kwargs['chat_room_id'])
        context.update({"chat_room": chat_room})
        return context
