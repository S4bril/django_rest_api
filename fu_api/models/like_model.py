from django.db import models
from django.utils.timezone import now


class Like(models.Model):
    sender = models.ForeignKey(
        "CustomUser",
        related_name="sent_likes",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    receiver = models.ForeignKey(
        "CustomUser",
        related_name="received_likes",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    created_at = models.DateTimeField(default=now)
