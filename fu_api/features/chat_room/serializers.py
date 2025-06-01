from rest_framework import serializers

from fu_api.features.messages.serializers import MessageSerializer
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.custom_user_model import CustomUser


class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    newest_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ["id", "name", "is_group", "members", "newest_message"]
        read_only_fields = ["new_message"]

    def get_newest_message(self, obj):
        latest_message = obj.messages.order_by("timestamp").first()
        if latest_message:
            return MessageSerializer(latest_message).data
        return None


class ChatRoomMemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["username", "image_url", "is_admin"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request and obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_is_admin(self, obj):
        chat_room = self.context.get("chat_room")
        if chat_room:
            return chat_room.admins.filter(id=obj.id).exists()
        return False
