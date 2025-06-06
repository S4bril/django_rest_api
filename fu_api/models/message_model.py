from django.db import models

from fu_api.models.custom_user_model import CustomUser
from fu_api.models.private_chat_room_model import PrivateChatRoom


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="messages"
    )
    chat_room = models.ForeignKey(
        PrivateChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}..."
