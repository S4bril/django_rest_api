from rest_framework import serializers

from fu_api.features.common.serializers.friend_serializer import FriendSerializer
from fu_api.models.friend_request_model import FriendRequest


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "status", "created_at"]
        read_only_fields = ["id", "sender", "status", "created_at"]


class FriendRequestCreateSerializer(serializers.Serializer):
    receiver = serializers.IntegerField()


class FriendRequestUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["accepted", "rejected"])
