from rest_framework import serializers
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.chat_room_model import ChatRoom


class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ["id", "name", "is_group", "members"]

    def validate(self, data):
        user = self.context["request"].user
        members = data.get("members", [])
        is_group = data.get("is_group", False)

        non_friend_members_ids = [
            member for member in members 
            if not user.friends.filter(id=member).exists()
        ]
        if non_friend_members_ids:
            raise serializers.ValidationError({
                "members": f"Users {non_friend_members_ids} are not your friends."
            })

        if is_group and len(members) < 1:
            raise serializers.ValidationError("A group chat must have at least one member.")

        if not is_group and len(members) != 1:
            raise serializers.ValidationError("A private chat must have exactly one member.")

        return data

    def create(self, validated_data):
        members_ids = validated_data.pop("members")
        user = self.context["request"].user  

        chat_room = ChatRoom.objects.create(**validated_data)
        chat_room.members.add(user, *CustomUser.objects.filter(id__in=members_ids))

        return chat_room
