import os
import json
import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import CustomUser, Event, Location

from datetime import date


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(BASE_DIR, 'json_forms/passions.json')

with open(json_file_path, 'r') as file:
    PASSIONS = json.load(file)['passions']

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if data.startswith('/9j'):
                imgstr = data   
                ext = 'jpeg'
            elif data.startswith('iVBORw0KGgo'):
                imgstr = data
                ext = 'png'
            else:
                raise serializers.ValidationError("Unsupported image format")

        image_data = base64.b64decode(imgstr)
        data = ContentFile(image_data, name=f'temp.{ext}')
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
    profile_image = Base64ImageField(write_only=True)
    image_url = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    sex_id = serializers.IntegerField(write_only=True)
    passions = serializers.SerializerMethodField()
    friend_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'birthday', 'bio', 'password', 'profile_image', 'image_url',
                  'owned_events', 'participated_events', 'passions', 'created_at', 'friend_count', 'sex', 'sex_id']
        read_only_fields = ['sex', 'id', 'account_creation_date', 'image_url', 'owned_events', 'participated_events', 'friend_count']

    def get_sex(self, obj):
        return obj.get_sex_id_display()

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
    
    def get_passions(self, obj):
        passions_ids = obj.passions
        passions_names = [PASSIONS.get(str(p_id), {}).get('name', 'Unknown') for p_id in passions_ids]
        return passions_names
    
    def get_friend_count(self, obj):
        return obj.friends.count()


class FriendSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['username', 'sex', 'bio', 'image_url', 'age']

    def get_sex(self, obj):
        return obj.get_sex_display()
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_age(self, obj):
        if obj.birthday:
            today = date.today()
            age = today.year - obj.birthday.year - (
                (today.month, today.day) < (obj.birthday.month, obj.birthday.day)
            )
            return age
        return None

