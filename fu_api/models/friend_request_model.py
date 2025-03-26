from django.db import models
from fu_api.models.custom_user_model import CustomUser


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

    def save(self, *args, **kwargs):
        if self.sender == self.receiver:
            raise ValueError("Users cannot send friend requests to themselves.")
        super().save(*args, **kwargs)

    def accept(self):
        self.status = 'accepted'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def __str__(self):
        return f"FriendRequest from {self.sender.username} to {self.receiver.username} [{self.status}]"