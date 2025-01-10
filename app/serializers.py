from base64 import b64decode

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import CustomUser, Event, Location


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'owner', 'participants', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'latitude', 'longitude', 'updated_at']

    def validate(self, data):
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if (-180.0 > longitude > 180.0):
            raise serializers.ValidationError("longitude has to be in range from -180 degrees to 180 degrees")

        if (-90.0 > latitude > 90.0):
            raise serializers.ValidationError("latitude has to be in range from -90.0 degrees to 90.0 degrees")
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_image = Base64ImageField(required=False, write_only=True)
    image_url = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    # passions = serializers.SerializerMethodField() # todo

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'sex', 'birthday', 'bio', 'password', 'profile_image', 'image_url', 
                  'owned_events', 'participated_events', 'passions']
        read_only_fields = ['id', 'account_creation_date', 'image_url', 'owned_events', 'participated_events']
        
    def get_sex(self, obj):
        return obj.get_sex_display()

    def create(self, validated_data):
        _ = validated_data.pop('friends', None)
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password', None))

        if 'image' in validated_data:
            profile_image = validated_data.pop('profile_image', None)
            if profile_image:
                instance.profile_image = profile_image

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
    
        instance.save()
    
        return instance
    
    def get_image_url(self, obj):
        if obj.profile_image:
            return self.context['request'].build_absolute_uri(obj.profile_image.url)
        return None


class FriendSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'sex', 'birthday', 'bio', 'account_creation_date', 'image_url', 'owned_events', 'participated_events']

    def get_sex(self, obj):
        return obj.get_sex_display()
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None
