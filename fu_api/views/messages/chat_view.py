from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.notification_model import Notification
from fu_api.serializers.chat_room_serializer import ChatRoomSerializer


class ChatRoomListCreateView(ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        chat_room = serializer.save()

        for member in chat_room.members.all():
            if member != self.request.user:
                Notification.objects.create(
                    user=member,
                    sender=self.request.user,
                    type="chat_invite",
                    message=f"You have been added to the chat: {chat_room.name}."
                )
