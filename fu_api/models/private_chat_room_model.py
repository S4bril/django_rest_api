from django.db import models

from fu_api.models.custom_user_model import CustomUser


class PrivateChatRoom(models.Model):
    members = models.ManyToManyField(CustomUser, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
