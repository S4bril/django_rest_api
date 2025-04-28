from django.db import models
from fu_api.models.custom_user_model import CustomUser


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    is_group = models.BooleanField(default=False)
    members = models.ManyToManyField(CustomUser, related_name="chat_rooms")
    admins = models.ManyToManyField(CustomUser, related_name="admin_chat_rooms")

    def __str__(self):
        return self.name if self.name else f"Chat {self.id}"
