from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions
from fu_api.models.chat_room_model import ChatRoom
from fu_api.serializers.chat_room_serializer import ChatRoomSerializer


class ChatRoomListCreateView(ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

