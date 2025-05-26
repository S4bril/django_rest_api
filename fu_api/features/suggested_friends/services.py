from fu_api.models.like_model import Like
from fu_api.models.match_model import Match
from fu_api.models.notification_model import Notification
from django.db.models import Q


class LikeService:
    @staticmethod
    def create_like(sender, receiver):
        if sender == receiver:
            raise ValueError("Sender and receiver must be different users.")
        
        if Match.objects.filter(
            Q(first_user=sender, second_user=receiver) |
            Q(first_user=receiver, second_user=sender)
        ).exists():
            raise ValueError("You are already matched with this user.")

        mutual_like = Like.objects.filter(sender=receiver, receiver=sender).first()

        if mutual_like:
            mutual_like.delete()

            #needed for excluding from suggested friends:
            sender.friends.add(receiver) 

            match = Match.objects.create(first_user=sender, second_user=receiver)

            Notification.objects.create(
                user=receiver,
                sender=sender,
                type='match',
                message=f"Ty i {sender.username} zostaliście dopasowani!"
            )
            Notification.objects.create(
                user=sender,
                sender=receiver,
                type='match',
                message=f"Ty i {receiver.username} zostaliście dopasowani!"
            )

            return {'match': match}

        like = Like.objects.create(sender=sender, receiver=receiver)

        Notification.objects.create(
            user=receiver,
            sender=sender,
            type='like',
            message=f"{sender.username} polubił twój profil."
        )

        return {'like': like}
