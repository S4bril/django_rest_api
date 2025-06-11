from django.db import models

from fu_api.models.custom_user_model import CustomUser


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        (
            "first_message",
            "First Message",
        ),  # dostajesz jak ktoś wyśle do cb pierwszą wiadomość
        (
            "like",
            "Like",
        ),  # dostajesz jak ktoś cię polubi ale ty jeszcze tej osoby nie polubiłeś
        ("match", "Match"),  # dostajesz jak powstanie match po tym jak ktoś cię polubił
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="notifications"
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.type}"

    def save(self, *args, **kwargs):
        if not self.message:
            self.message = self.generate_message()
        super().save(*args, **kwargs)

    def generate_message(self):
        if self.type == "first_message":
            return f"{self.sender.username} wysłał(a) Ci pierwszą wiadomość."
        elif self.type == "like":
            return f"{self.sender.username} polubił(a) Cię."
        elif self.type == "match":
            return f"Masz nowego matcha z {self.sender.username}!"
        else:
            return "Masz nowe powiadomienie."
