from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.custom_user_model import CustomUser


class AddMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id):
        user_id = request.data.get("user_id")

        try:
            new_member = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": f"User with id: {user_id} not found"}, status=404)

        if new_member not in request.user.friends.all():
            return Response({"error": f"User with id: {user_id} is not your friend"}, status=400)

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id, is_group=True)
        except ChatRoom.DoesNotExist:
            return Response({"error": f"Chat room with id: {chat_room_id} not found or is not a group."}, status=404)

        if request.user not in chat_room.members.all():
            return Response({"error": "You are not in this group"}, status=403)

        if new_member in chat_room.members.all():
            return Response({"error": "User is already in the chat"}, status=400)

        chat_room.members.add(new_member)
        #NOTIFICATION
        return Response({"message": "Member added successfully"}, status=200)


