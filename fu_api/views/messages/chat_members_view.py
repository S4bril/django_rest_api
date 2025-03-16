# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from fu_api.models.chat_room_model import ChatRoom
from fu_api.serializers.friend_serializers import FriendSerializer

class ChatRoomMembersView(APIView):
    def get(self, request, chat_room_id):
        try:
            chat_room = ChatRoom.objects.get(pk=chat_room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": f"Chat room with id: {chat_room_id} not found."}, status=404)
        members = chat_room.members.all()
        serializer = FriendSerializer(members, many=True)
        return Response(serializer.data)