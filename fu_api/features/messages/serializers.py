from rest_framework import serializers

from fu_api.features.common.serializers.friend_serializer import FriendSerializer
from fu_api.models.message_model import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender_id", "content", "created_at"]
        read_only_fields = ["id", "sender_id", "created_at"]
