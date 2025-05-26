from django.db import models
from django.utils.timezone import now


class Match(models.Model):
    first_user = models.OneToOneField(
        'CustomUser',
        related_name='sent_match',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    second_user = models.OneToOneField(
        'CustomUser',
        related_name='received_match',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    created_at = models.DateTimeField(default=now)
