from rest_framework import serializers
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.models import CustomUser
from fu_api.models.like_model import Like
from fu_api.models.match_model import Match
from fu_api.models.notification_model import Notification


class LikeSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)

    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='receiver', write_only=True
    )

    class Meta:
        model = Like
        fields = ['id', 'sender', 'receiver_id']

    def validate(self, data):
        sender = self.context['request'].user
        receiver = data['receiver']

        if sender == receiver:
            raise serializers.ValidationError("Sender and receiver must be different users.")

        if Like.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError("You have already liked this user.")

        return data

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver = validated_data['receiver']

        if Like.objects.filter(sender=receiver, receiver=sender).exists():
            Like.objects.filter(sender=receiver, receiver=sender).delete()

            Match.objects.create(
                first_user=receiver,
                second_user=sender,
            )

            Notification.objects.create(
                user=receiver,
                sender=sender,
                type='match',
                message=f"{sender.username} jest twoim nowym znajomym."
            )
        else:
            like = Like.objects.create(sender=sender, receiver=receiver)
            Notification.objects.create(
                user=receiver,
                sender=sender,
                type='like',
                message=f"{sender.username} polubił twój profil."
            )

        return like


class MatchSerializer(serializers.ModelSerializer):
    matched_user = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ['id', 'created_at', 'matched_user']

    def get_matched_user(self, obj):
        request_user = self.context['request'].user
        other_user = obj.second_user if obj.first_user == request_user else obj.first_user

        return FriendSerializer(other_user).data
