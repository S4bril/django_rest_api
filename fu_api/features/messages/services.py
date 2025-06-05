from rest_framework.exceptions import ValidationError

from fu_api.models.message_model import Message
from fu_api.models.notification_model import Notification


class MessageService:
    @staticmethod
    def send_message(sender, chat_room, content):
        MessageService._ensure_member(chat_room, sender)
        MessageService._ensure_not_blocked_in_private(chat_room, sender)

        message = Message.objects.create(
            sender=sender, chat_room=chat_room, content=content
        )

        recipients = chat_room.members.exclude(id=sender.id)
        notifications = [
            Notification(
                user=member,
                sender=sender,
                type="message",
                message=f"Masz nieprzeczytane wiadomości od: {sender.username}.",
            )
            for member in recipients
        ]
        Notification.objects.bulk_create(notifications)

        return message

    @staticmethod
    def _ensure_member(chat_room, user):
        if not chat_room.members.filter(id=user.id).exists():
            raise ValidationError({"error_msg": "Nie jesteś uczestnikiem tego czatu."})

    @staticmethod
    def _ensure_not_blocked_in_private(chat_room, user):
        other = chat_room.members.exclude(id=user.id).first()
        if other and user in other.blocked_users.all():
            raise ValidationError(
                {"error_msg": f"Jesteś zablokowany przez {other.username}."}
            )
