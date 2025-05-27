from rest_framework import serializers
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.models import CustomUser
from fu_api.models.like_model import Like
from fu_api.models.match_model import Match


class LikeSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)

    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='receiver', write_only=True
    )

    class Meta:
        model = Like
        fields = ['id', 'sender', 'receiver_id']


class MatchSerializer(serializers.ModelSerializer):
    matched_user = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ['id', 'created_at', 'matched_user']

    def get_matched_user(self, obj):
        request_user = self.context['request'].user
        other_user = obj.second_user if obj.first_user == request_user else obj.first_user

        return FriendSerializer(other_user).data
