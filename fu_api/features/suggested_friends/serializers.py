from datetime import date
import json
import os
from rest_framework import serializers
from config import settings
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.models import CustomUser
from fu_api.features.suggested_friends.matchers.feature_engineer import FeatureEngineer
from fu_api.models.like_model import Like
from fu_api.models.match_model import Match
from fu_api.models.notification_model import Notification


class SuggestedFriendSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    passions = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    friend_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'sex', 'bio', 'image_url', 'age', 'passions', 'distance', 'friend_count']

    def get_friend_count(self, obj):
        return obj.friends.count()

    def get_distance(self, obj):
        current_user = self.context.get('current_user')
        feature_engineer = FeatureEngineer()
        return feature_engineer.compute_distance(current_user, obj)

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
        passions_file_path = os.path.join(settings.BASE_DIR, "fu_api", "json_forms", "passions.json")
        with open(passions_file_path, 'r', encoding="utf-8") as file:
            passions = json.load(file)['passions']
        passions_names = [passions.get(str(p_id), {}).get('name', 'Unknown') for p_id in obj.passions_ids]
        return passions_names


class LikeSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)

    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='receiver', write_only=True
    )

    class Meta:
        model = Like
        fields = ['id', 'sender', 'receiver_id']

    def validate(self, data):
        sender = self.context['request'].user
        receiver = data['receiver']

        if sender == receiver:
            raise serializers.ValidationError("Sender and receiver must be different users.")

        if Like.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError("You have already liked this user.")

        return data

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver = validated_data['receiver']

        if Like.objects.filter(sender=receiver, receiver=sender).exists():
            Like.objects.filter(sender=receiver, receiver=sender).delete()

            Match.objects.create(
                first_user=receiver,
                second_user=sender,
            )

            Notification.objects.create(
                user=receiver,
                sender=sender,
                type='match',
                message=f"{sender.username} jest twoim nowym znajomym."
            )
        else:
            like = Like.objects.create(sender=sender, receiver=receiver)
            Notification.objects.create(
                user=receiver,
                sender=sender,
                type='like',
                message=f"{sender.username} polubił twój profil."
            )

        return like


class MatchSerializer(serializers.ModelSerializer):
    matched_user = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ['id', 'created_at', 'matched_user']

    def get_matched_user(self, obj):
        request_user = self.context['request'].user
        other_user = obj.second_user if obj.first_user == request_user else obj.first_user

        return FriendSerializer(other_user).data
