from rest_framework import serializers

from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        # friends = validated_data.pop('friends', None)
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        # if friends is not None:
        #     user.friends.set(friends)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        friends_to_add = validated_data.pop('friends_to_add', None)
        friends_to_remove = validated_data.pop('friends_to_remove', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if friends_to_add is not None:
            instance.friends.add(*friends_to_add)
        
        if friends_to_remove is not None:
            instance.friends.remove(*friends_to_remove)

        instance.save()
        return instance

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'date_joined', 'email', 'date_of_birth', 'bio', 'friends', 'password']