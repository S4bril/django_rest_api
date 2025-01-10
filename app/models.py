from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.conf import settings
from django.db import models


class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    sex_id = models.IntegerField(choices=[(0, 'Mężczyzna'), (1, 'Kobieta'),], blank=False, null=False)
    birthday = models.DateField(blank=False, null=False)
    bio = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(default=now)
    friends = models.ManyToManyField("self", blank=True, symmetrical=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=False, null=False)

    location = models.OneToOneField(
        'Location',
        related_name='user_location',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    passions = models.JSONField(
        blank=False,
        null=False,
        default=list,
    )

    rejected_users = models.ManyToManyField("self", blank=True, symmetrical=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username}"


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_events"
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_events",
        blank=True
    )

    location = models.OneToOneField(
        'Location',
        related_name='event_location',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
