from django.db import models
from django.utils.timezone import now


class Match(models.Model):
    user1 = models.ForeignKey(
        "CustomUser",
        related_name="matches_initiated",
        on_delete=models.CASCADE,
    )
    user2 = models.ForeignKey(
        "CustomUser",
        related_name="matches_received",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = (("user1", "user2"),)

    def save(self, *args, **kwargs):
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)
