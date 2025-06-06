import random

from django.core.exceptions import ValidationError
from django.db import migrations

from fu_api.features.suggested_friends.services import LikeService
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.like_model import Like
from fu_api.models.match_model import Match

NUM_TO_LIKE = 20
NUM_TO_BE_LIKED = 20
NUM_TO_MATCH = 10


def seed_user1_relationships(apps, schema_editor):
    try:
        user1 = CustomUser.objects.get(pk=1)
    except CustomUser.DoesNotExist:
        return

    all_others = list(CustomUser.objects.exclude(pk=1))

    _seed_likes_by_user1(user1, all_others)

    remaining = [
        u
        for u in all_others
        if not Like.objects.filter(sender=user1, receiver=u).exists()
    ]
    _seed_likes_to_user1(user1, remaining)

    liked_ids = set(
        Like.objects.filter(sender=user1).values_list("receiver_id", flat=True)
    )
    liked_by_ids = set(
        Like.objects.filter(receiver=user1).values_list("sender_id", flat=True)
    )
    excluded_ids = liked_ids.union(liked_by_ids) | {user1.id}

    pool_for_match = [u for u in all_others if u.id not in excluded_ids]
    _seed_matches(user1, pool_for_match)


def _seed_likes_by_user1(user1, pool):
    to_like = random.sample(pool, min(len(pool), NUM_TO_LIKE))
    for u in to_like:
        if Like.objects.filter(sender=user1, receiver=u).exists():
            continue
        try:
            LikeService.create_like(sender=user1, receiver=u)
        except ValidationError:
            continue


def _seed_likes_to_user1(user1, pool):
    to_be_liked = random.sample(pool, min(len(pool), NUM_TO_BE_LIKED))
    for u in to_be_liked:
        if Like.objects.filter(sender=u, receiver=user1).exists():
            continue
        try:
            LikeService.create_like(sender=u, receiver=user1)
        except ValidationError:
            continue


def _seed_matches(user1, pool):
    to_match = random.sample(pool, min(len(pool), NUM_TO_MATCH))
    for u in to_match:
        if (
            Match.objects.filter(user1=user1, user2=u).exists()
            or Match.objects.filter(user1=u, user2=user1).exists()
        ):
            continue
        try:
            Match.objects.create(user1=user1, user2=u)
            user1.friends.add(u)
        except ValidationError:
            continue


class Migration(migrations.Migration):
    dependencies = [
        ("fu_api", "0003_assign_profile_images"),
    ]

    operations = [
        migrations.RunPython(seed_user1_relationships),
    ]
