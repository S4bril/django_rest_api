from rest_framework import serializers

from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.notification_model import Notification

class FriendRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status']
        read_only_fields = ['sender', 'receiver']

    def update(self, instance, validated_data):
        request_user = self.context['request'].user

        if instance.receiver != request_user:
            raise serializers.ValidationError("You are not authorized to respond to this friend request.")

        if instance.status != 'pending':
            raise serializers.ValidationError("This friend request has already been processed.")

        if 'status' in validated_data:
            if validated_data['status'] == 'accepted':
                instance.accept()

                Notification.objects.create(
                    user=instance.sender,
                    sender=request_user,
                    type='friend_request',
                    message=f"{request_user.username} accepted your friend request."
                )

            elif validated_data['status'] == 'rejected':
                instance.reject()

                Notification.objects.create(
                    user=instance.sender,
                    sender=request_user,
                    type='friend_request',
                    message=f"{request_user.username} rejected your friend request."
                )

        return instance
