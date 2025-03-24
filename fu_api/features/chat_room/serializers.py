from django.shortcuts import get_object_or_404
from rest_framework import serializers
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.notification_model import Notification


class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "name", "is_group", "members"]

    def validate(self, data):
        user = self.context["request"].user
        members = data.get("members", [])
        is_group = data.get("is_group", False)

        if user.id in members:
            raise serializers.ValidationError({"members": "You cannot add yourself to the members list."})

        blocked_ids = []
        for member_id in members:
            target = CustomUser.objects.filter(id=member_id).first()
            if target:
                if user in target.blocked_users.all():
                    blocked_ids.append(member_id)
                elif target in user.blocked_users.all():
                    blocked_ids.append(member_id)
        if blocked_ids:
            raise serializers.ValidationError({
                "members": "Some users blocked you.",
                "blocked_by": f"{blocked_ids}" 
            })

        if is_group and len(members) < 1:
            raise serializers.ValidationError({"members": "A group chat must have at least one member."})

        return data

    def create(self, validated_data):
        members_ids = validated_data.pop("members")
        user = self.context["request"].user  

        chat_room = ChatRoom.objects.create(**validated_data)
        chat_room.members.add(user, *CustomUser.objects.filter(id__in=members_ids))

        for member in chat_room.members.all():
            if member != user:
                Notification.objects.create(
                    user=member,
                    sender=user,
                    type="chat_invite",
                    message=f"You have been added to the chat: {chat_room.name}."
                )
        return chat_room
