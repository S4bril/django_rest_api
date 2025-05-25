import base64
import json
import os

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers
from sentence_transformers import SentenceTransformer
from fu_api.models.custom_user_model import CustomUser


bio_encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

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


class UserSerializer(serializers.ModelSerializer):
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
        password = validated_data.pop('password')
        bio_text = validated_data.get('bio', '')

        bio_embedding = bio_encoder.encode(bio_text).tolist()
        validated_data['bio_embedding'] = bio_embedding

        user = super().create(validated_data)

        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password', None))

        if 'image' in validated_data: #romve old one?
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
        passions_file_path = os.path.join(settings.BASE_DIR, "fu_api", "json_forms", "passions.json")
        with open(passions_file_path, 'r', encoding="utf-8") as file:
            passions = json.load(file)['passions']
        passions_names = [passions.get(str(p_id), {}).get('name', 'Unknown') for p_id in passions_ids]
        return passions_names

    def get_friend_count(self, obj):
        return obj.friends.count()
