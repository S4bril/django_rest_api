import os
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

from .location_model import Location

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    sex_id = models.IntegerField(
        choices=[
            (0, "Mężczyzna"),
            (1, "Kobieta"),
        ],
        blank=False,
        null=False,
        default=0,
    )
    birthday = models.DateField(blank=False, null=False, default=date.today)
    bio = models.TextField(blank=False, null=False, default='')
    created_at = models.DateTimeField(default=now)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    blocked_users = models.ManyToManyField("self", blank=True, symmetrical=False)
    rejected_users = models.ManyToManyField("self", blank=True, symmetrical=True)
    bio_embedding = models.JSONField(null=False, blank=False, default=dict)

    location = models.OneToOneField(
        Location,
        related_name="user",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    passions_ids = models.JSONField(
        blank=False,
        null=False,
        default=list,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.username}"

    def delete(self, *args, **kwargs):
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)

        if self.location:
            self.location.delete()
        super().delete(*args, **kwargs)