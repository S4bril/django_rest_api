from rest_framework import serializers

from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.models.message_model import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "content", "timestamp"]
        read_only_fields = ["id", "sender", "timestamp"]
