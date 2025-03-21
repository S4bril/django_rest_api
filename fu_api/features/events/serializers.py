from rest_framework import serializers
from fu_api.models.event_model import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'owner', 'participants', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']