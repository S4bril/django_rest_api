from rest_framework import serializers
from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.notification_model import Notification


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']
        read_only_fields = ['sender', 'status', 'created_at']

    def validate(self, data):
        sender = self.context['request'].user
        receiver = data['receiver']

        if sender == receiver:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")

        if sender in receiver.blocked_users.all():
            raise serializers.ValidationError(f"You are blocked by {receiver.username}.")

        if receiver in sender.friends.all():
            raise serializers.ValidationError("User is already your friend.")

        if FriendRequest.objects.filter(sender=sender, receiver=receiver, status='pending').exists():
            raise serializers.ValidationError("Friend request already sent.")

        if FriendRequest.objects.filter(sender=sender, receiver=receiver, status='rejected').exists():
            raise serializers.ValidationError("Friend request was previously rejected.")

        return data

    def create(self, validated_data):
        friend_request = FriendRequest.objects.create(
            sender=self.context['request'].user,
            receiver=validated_data['receiver']
        )

        Notification.objects.create(
            user=friend_request.receiver,
            sender=friend_request.sender,
            type='friend_request',
            message=f"{friend_request.sender.username} sent you a friend request."
        )

        return friend_request
