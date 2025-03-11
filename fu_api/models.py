import os
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
    friends = models.ManyToManyField("self", blank=True, symmetrical=True) # what if I deleted my account?
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    rejected_users = models.ManyToManyField("self", blank=True, symmetrical=True) # what if I deleted my account?

    location = models.OneToOneField(
        'Location',
        related_name='user',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    passions = models.JSONField(
        blank=False,
        null=False,
        default=list,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username}"
    
    def delete(self, *args, **kwargs): #maybe do this with signals
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)

        if self.location:
            self.location.delete()
        super().delete(*args, **kwargs)


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_friend_requests")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def save(self, *args, **kwargs):
        if self.sender == self.receiver:
            raise ValueError("Users cannot send friend requests to themselves.")
        super().save(*args, **kwargs)

    def accept(self):
        self.status = 'accepted'
        self.sender.friends.add(self.receiver)
        self.receiver.friends.add(self.sender)
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def __str__(self):
        return f"FriendRequest from {self.sender.username} to {self.receiver.username} [{self.status}]"


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    #add image

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
        related_name='event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs): #maybe do this with signals
        if self.location:
            self.location.delete()
        super().delete(*args, **kwargs)
