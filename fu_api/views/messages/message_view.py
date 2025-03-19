from urllib import response
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.message_model import Message 
from fu_api.models.notification_model import Notification
from fu_api.serializers.message_serializer import MessageSerializer


class MessageListCreateView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        return Message.objects.filter(chat_room_id=chat_room_id)

    def perform_create(self, serializer):
        chat_room = ChatRoom.objects.get(id=self.kwargs['chat_room_id'])
        if self.request.user not in chat_room.members.all():
            return response({'error': 'You are not a member of this chat'}, status=403)
        serializer.save(sender=self.request.user, chat_room=chat_room)

        for member in chat_room.members.all():
            if member != self.request.user:
                Notification.objects.create(
                    user=member,
                    sender=self.request.user,
                    type='message',
                    message=f"You have a new unread message!"
                )
