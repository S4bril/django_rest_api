import random
from datetime import timedelta
from django.db import migrations
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from fu_api.models.custom_user_model import CustomUser
from fu_api.models.notification_model import Notification
from fu_api.models.private_chat_room_model import PrivateChatRoom


NUM_TO_LIKE = 20
NUM_TO_BE_LIKED = 20


def seed_user1_relationships(apps, schema_editor):
    """
    Dla usera o id=1:
      a) user1 „polubi” losowych użytkowników → tworzymy Notification typu 'like',
      b) user1 zostanie „polubiony” przez losowych użytkowników → również Notification typu 'like',
         ale odwrotnie: sender=other, user=user1,
      c) user1 zostanie sparowany/przyjacielem (i „zmatchowany”) z kolejnymi losowymi
         użytkownikami, wyłączając tych, którzy pojawili się w a) lub b) → tworzymy ChatRoom (is_group=False).
    """

    user1 = CustomUser.objects.get(pk=1)

    all_others = list(CustomUser.objects.exclude(pk=1))



    liked_users = random.sample(all_others, NUM_TO_LIKE)

    for u in liked_users:
        Notification.objects.create(
            user=u,
            sender=user1,
            type="like",
            message=f"User {user1.username} polubił użytkownika {u.username}",
            created_at=timezone.now() - timedelta(minutes=random.randint(0, 60)),
        )

    remaining = [u for u in all_others if u not in liked_users]
    liked_by_users = random.sample(remaining, NUM_TO_BE_LIKED)

    for u in liked_by_users:
        Notification.objects.create(
            user=user1,
            sender=u,
            type="like",
            message=f"Użytkownik {u.username} polubił usera {user1.username}",
            created_at=timezone.now() - timedelta(minutes=random.randint(0, 60)),
        )

    excluded = set(liked_users) | set(liked_by_users) | {user1}
    pool_for_matches = [u for u in all_others if u not in excluded]

    num_to_match = min(3, len(pool_for_matches))
    matched_users = random.sample(pool_for_matches, num_to_match)

    for u in matched_users:
        chat = PrivateChatRoom.objects.create(name=None, is_group=False)
        chat.members.add(user1, u)
        Notification.objects.create(
            user=user1,
            sender=u,
            type="match",
            message=f"Użytkownik {u.username} i {user1.username} są teraz przyjaciółmi!",
            created_at=timezone.now(),
        )
        Notification.objects.create(
            user=u,
            sender=user1,
            type="match",
            message=f"Użytkownik {user1.username} i {u.username} są teraz przyjaciółmi!",
            created_at=timezone.now(),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("fu_api", "0003_assign_profile_images")
    ]

    operations = [
        migrations.RunPython(seed_user1_relationships),
    ]
