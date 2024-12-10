from rest_framework import serializers

from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    friend_to_add = serializers.IntegerField(required=False, write_only=True)
    friend_to_remove = serializers.IntegerField(required=False, write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        friend_to_add = validated_data.pop('friend_to_add', None)
        friend_to_remove = validated_data.pop('friend_to_remove', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if friend_to_add:
            instance.friends.add(friend_to_add)

        if friend_to_remove:
            instance.friends.remove(friend_to_remove)

        instance.save()
        return instance

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 
                  'date_joined', 'email', 'date_of_birth', 'bio', 
                  'friends', 'password', 'friend_to_add', 'friend_to_remove']