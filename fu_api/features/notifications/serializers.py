from rest_framework import serializers
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.models.notification_model import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "sender", "type", "message", "is_read", "created_at"]
