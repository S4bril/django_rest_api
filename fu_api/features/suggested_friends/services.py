from django.db.models import Q

from fu_api.models.like_model import Like
from fu_api.models.match_model import Match
from fu_api.models.notification_model import Notification


class LikeService:
    @staticmethod
    def create_like(sender, receiver):
        if sender == receiver:
            raise ValueError("Sender and receiver must be different users.")

        if Like.objects.filter(sender=sender, receiver=receiver).exists():
            raise ValueError("You already liked this user.")

        if Match.objects.filter(
            Q(user1=sender, user2=receiver) | Q(user1=receiver, user2=sender)
        ).exists():
            raise ValueError("You are already matched with this user.")

        mutual_like = Like.objects.filter(sender=receiver, receiver=sender).first()

        if mutual_like:
            mutual_like.delete()

            # needed for excluding from suggested friends:
            sender.friends.add(receiver)

            match = Match.objects.create(user1=sender, user2=receiver)

            Notification.objects.create(
                user=receiver,
                sender=sender,
                type="match",
                message=f"Ty i {sender.username} zostaliście dopasowani!",
            )
            Notification.objects.create(
                user=sender,
                sender=receiver,
                type="match",
                message=f"Ty i {receiver.username} zostaliście dopasowani!",
            )

            return {"match": match}

        like = Like.objects.create(sender=sender, receiver=receiver)

        Notification.objects.create(
            user=receiver,
            sender=sender,
            type="like",
            message=f"{sender.username} polubił twój profil.",
        )

        return {"like": like}
