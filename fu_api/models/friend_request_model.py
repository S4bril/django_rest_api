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

    class Meta:
        unique_together = ('sender', 'receiver')

    def save(self, *args, **kwargs):
        if self.sender == self.receiver:
            raise ValueError("Users cannot send friend requests to themselves.")
        
        existing_request = FriendRequest.objects.filter(sender=self.sender, receiver=self.receiver).first()

        if existing_request:
            if existing_request.status == 'rejected':
                existing_request.delete()
            elif existing_request.status == 'accepted' and self.receiver not in self.sender.friends.all():
                existing_request.delete()
            else:
                raise ValueError("Friend request already sent or still active.")
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