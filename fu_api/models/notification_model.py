from django.db import models
from fu_api.models.custom_user_model import CustomUser


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("friend_request", "Friend Request"),
        ("message", "Message"),
        ("chat_invite", "Chat Invite"),
        ("like", "Like"),
        ("match", "Match"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.type}"
