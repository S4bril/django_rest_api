from rest_framework import serializers
from fu_api.models.notification_model import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "sender", "sender_username", "type", "message", "is_read", "created_at"]
