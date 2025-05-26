from rest_framework import serializers
from fu_api.models.message_model import Message
from fu_api.models.notification_model import Notification

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ["sender", "chat_room"]

    def validate(self, data):
        chat_room = self.context.get("chat_room")
        request_user = self.context.get("request").user

        if request_user not in chat_room.members.all():
            raise serializers.ValidationError("You are not a member of this chat.")

        if not chat_room.is_group:
            other_members = chat_room.members.exclude(id=request_user.id)
            for member in other_members:
                if request_user in member.blocked_users.all():
                    raise serializers.ValidationError(f"You are blocked by {member.username}.")
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        chat_room = self.context["chat_room"]

        message = Message.objects.create(sender=user, chat_room=chat_room, **validated_data)

        for member in chat_room.members.all():
            if member != user:
                Notification.objects.create(
                    user=member,
                    sender=user,
                    type='message',
                    message=f"Masz nieprzeczytane wiadomości od: {chat_room.name}."
                )
        return message
