from datetime import date
from rest_framework import serializers
from fu_api.models import CustomUser


class FriendSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['username', 'sex', 'bio', 'image_url', 'age']

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
