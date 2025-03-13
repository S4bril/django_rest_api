from rest_framework import serializers
from fu_api.models.friend_request_model import FriendRequest


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'