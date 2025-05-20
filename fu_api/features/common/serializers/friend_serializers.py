from datetime import date
import json
import os
from rest_framework import serializers
from config import settings
from fu_api.models import CustomUser


class FriendSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    passions = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'sex', 'bio', 'image_url', 'age', 'passions']

    def get_sex(self, obj):
        return obj.get_sex_id_display()

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

    def get_passions(self, obj):
        passions_ids = obj.passions
        passions_file_path = os.path.join(settings.BASE_DIR, "fu_api", "json_forms", "passions.json")
        with open(passions_file_path, 'r', encoding="utf-8") as file:
            passions = json.load(file)['passions']
        passions_names = [passions.get(str(p_id), {}).get('name', 'Unknown') for p_id in passions_ids]
        return passions_names
