from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.notification_model import Notification


from django.forms import ValidationError


class FriendRequestService:
    @classmethod
    def create_request(cls, sender, receiver):
        if sender == receiver:
            raise ValidationError("You cannot send a friend request to yourself.")

        if receiver.blocked_users.filter(id=sender.id).exists():
            raise ValidationError(f"You are blocked by {receiver.username}.")

        if sender.friends.filter(id=receiver.id).exists():
            raise ValidationError("User is already your friend.")

        if FriendRequest.objects.filter(sender=sender, receiver=receiver, status='pending').exists():
            raise ValidationError("Friend request already sent.")

        if FriendRequest.objects.filter(sender=sender, receiver=receiver, status='rejected').exists():
            raise ValidationError("Friend request was previously rejected.")

        friend_request = FriendRequest.objects.create(sender=sender, receiver=receiver)

        cls._create_pending_notification(friend_request)

        return friend_request

    @classmethod
    def accept_request(cls, friend_request):
        if friend_request.status != 'pending':
            raise ValidationError("Cannot accept non-pending request")

        friend_request.status = 'accepted'
        friend_request.save()

        cls._create_friendship(friend_request.sender, friend_request.receiver)

        cls._create_update_status_notification(friend_request, 'accepted')

    @classmethod
    def reject_request(cls, friend_request):
        friend_request.status = 'rejected'
        friend_request.save()
        cls._create_update_status_notification(friend_request, 'rejected')

    @staticmethod
    def _create_friendship(user1, user2):
        user1.friends.add(user2)

    @staticmethod
    def _create_update_status_notification(request, status):
        Notification.objects.create(
            user=request.sender,
            sender=request.receiver,
            type='friend_request',
            message=f"{request.receiver.username} {status} your request."
        )

    @staticmethod
    def _create_pending_notification(request):
        Notification.objects.create(
            user=request.sender,
            sender=request.receiver,
            type='friend_request',
            message=f"{request.receiver.username} sent you friend request."
        )