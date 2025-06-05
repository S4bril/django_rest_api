from rest_framework import serializers

from fu_api.features.common.serializers.friend_serializer import FriendSerializer
from fu_api.features.messages.serializers import MessageSerializer
from fu_api.models.private_chat_room_model import PrivateChatRoom


class PrivateChatRoomSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField(read_only=True)
    newest_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PrivateChatRoom
        fields = ["id", "member", "newest_message"]

    def get_member(self, obj):
        request_user = self.context["request"].user
        other_member = obj.members.exclude(id=request_user.id).first()
        return FriendSerializer(other_member, context=self.context).data

    def get_newest_message(self, obj):
        latest_message = obj.messages.order_by("-created_at").first()
        if latest_message:
            return MessageSerializer(latest_message, context=self.context).data
        return None
