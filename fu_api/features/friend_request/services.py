from rest_framework.exceptions import PermissionDenied, ValidationError

from fu_api.models.friend_request_model import FriendRequest
from fu_api.models.notification_model import Notification


class FriendRequestService:
    @staticmethod
    def send_request(sender, receiver):
        FriendRequestService._ensure_not_self(sender, receiver)
        FriendRequestService._ensure_not_blocked(sender, receiver)
        FriendRequestService._ensure_not_already_friends(sender, receiver)
        FriendRequestService._ensure_no_pending_request(sender, receiver)
        FriendRequestService._ensure_not_previously_rejected(sender, receiver)

        friend_req = FriendRequest.objects.create(sender=sender, receiver=receiver)
        Notification.objects.create(
            user=receiver,
            sender=sender,
            type="friend_request",
            message=f"{sender.username} wysłał Ci zaproszenie do znajomych.",
        )
        return friend_req

    @staticmethod
    def respond_request(receiver, friend_req, status):
        if status == "accepted":
            friend_req.accept()
            receiver.friends.add(friend_req.sender)
        elif status == "rejected":
            friend_req.reject()

        msg = "zaakceptował/a" if status == "accepted" else "odrzucił/a"
        Notification.objects.create(
            user=friend_req.sender,
            sender=receiver,
            type="friend_request",
            message=f"{receiver.username} {msg} Twoje zaproszenie.",
        )
        return friend_req

    @staticmethod
    def _ensure_not_self(sender, receiver):
        if sender == receiver:
            raise ValidationError(
                {"error_msg": "Nie możesz wysłać zaproszenia do siebie."}
            )

    @staticmethod
    def _ensure_not_already_friends(sender, receiver):
        if receiver in sender.friends.all():
            raise ValidationError({"error_msg": "Jesteście już znajomymi."})

    @staticmethod
    def _ensure_no_pending_request(sender, receiver):
        if FriendRequest.objects.filter(
            sender=sender, receiver=receiver, status="pending"
        ).exists():
            raise ValidationError(
                {"error_msg": "Zaproszenie już wysłane i oczekuje na odpowiedź."}
            )

    @staticmethod
    def _ensure_not_previously_rejected(sender, receiver):
        if FriendRequest.objects.filter(
            sender=sender, receiver=receiver, status="rejected"
        ).exists():
            raise ValidationError(
                {"error_msg": "Twoje poprzednie zaproszenie zostało odrzucone."}
            )

    @staticmethod
    def _ensure_not_blocked(sender, receiver):
        if sender in receiver.blocked_users.all():
            raise PermissionDenied(
                {"error_msg": f"Zostałeś zablokowany przez {receiver.username}."}
            )
        if receiver in sender.blocked_users.all():
            raise PermissionDenied(
                {"error_msg": f"Odblokuj {receiver.username}, aby wysłać zaproszenie."}
            )
