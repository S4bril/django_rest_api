from rest_framework import serializers
from fu_api.models.message_model import Message

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ["sender", "chat_room"]