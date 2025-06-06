from rest_framework import serializers

from fu_api.features.common.serializers.friend_serializer import FriendSerializer
from fu_api.models.like_model import Like
from fu_api.models.match_model import Match


class LikeSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "sender"]


class MatchSerializer(serializers.ModelSerializer):
    matched_user = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ["id", "created_at", "matched_user"]

    def get_matched_user(self, obj):
        request_user = self.context["request"].user
        other_user = obj.user2 if obj.user1 == request_user else obj.user1

        return FriendSerializer(other_user).data
