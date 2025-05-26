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

        if not is_group:
            if len(members) != 1:
                raise serializers.ValidationError({"members": "A private chat room must have exactly one member.(Creator of group is added automatically)"})
            else:
                if user.id in members:
                    raise serializers.ValidationError({"members": "You cannot create private room with yourself."})

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
                "members": "Some users blocked you or there are blocked.",
                "blocked_by": f"{blocked_ids}" 
            })

        return data

    def create(self, validated_data):
        members_ids = validated_data.pop("members")
        user = self.context["request"].user  

        chat_room = ChatRoom.objects.create(**validated_data)
        chat_room.members.add(user, *CustomUser.objects.filter(id__in=members_ids))

        if chat_room.is_group:
            chat_room.admins.add(user)

        for member in chat_room.members.all():
            if member != user:
                Notification.objects.create(
                    user=member,
                    sender=user,
                    type="chat_invite",
                    message=f"Dodano Cię do czatu: {chat_room.name}."
                )
        return chat_room


class ChatRoomMemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'image_url', 'is_admin']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_is_admin(self, obj):
        chat_room = self.context.get('chat_room')
        if chat_room:
            return chat_room.admins.filter(id=obj.id).exists()
        return False
