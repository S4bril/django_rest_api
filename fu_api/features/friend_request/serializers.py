from rest_framework import serializers
from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.notification_model import Notification


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = "__all__"
        read_only_fields = ["sender"]

    def validate(self, data):
        sender = self.context["request"].user
        receiver = data["receiver"]

        if sender == receiver:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")

        if sender in receiver.blocked_users.all():
            raise serializers.ValidationError(f"You are blocked by {receiver.username}.")

        if receiver in sender.friends.all():
            raise serializers.ValidationError("User is already your friend.")

        if FriendRequest.objects.filter(sender=sender, receiver=receiver, status="pending").exists():
            raise serializers.ValidationError("Friend request already sent.")

        if FriendRequest.objects.filter(sender=sender, receiver=receiver, status="rejected").exists():
            raise serializers.ValidationError("Friend request was previously rejected.")

        return data

    def create(self, validated_data):
        friend_request = FriendRequest.objects.create(
            sender=self.context["request"].user,
            receiver=validated_data["receiver"]
        )
        Notification.objects.create(
            user=friend_request.receiver,
            sender=friend_request.sender,
            type="friend_request",
            message=f"{friend_request.sender.username} wysłał Ci zaproszenie do znajomych."
        )
        return friend_request


class FriendRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "status"]
        read_only_fields = ["sender", "receiver"]

    def update(self, instance, validated_data):
        if "status" in validated_data:
            if validated_data["status"] == "accepted":
                instance.accept()
                instance.receiver.friends.add(instance.sender)
                self._create_notification(instance, validated_data["status"])
            elif validated_data["status"] == "rejected":
                instance.reject()
                self._create_notification(instance, validated_data["status"])
            else:
                raise serializers.ValidationError("Status must be either 'accepted' or 'rejected'.")
        return instance

    def _create_notification(self, instance, status):
        polish = {
            "accepted": "zaakceptował/a",
            "rejected": "odrzucił/a"
        }
        return Notification.objects.create(
                user=instance.sender,
                sender=instance.receiver,
                type="friend_request",
                message=f"{instance.receiver.username} {polish[status]} your friend request."
            )
