import os

from django.conf import settings
from django.db import migrations

from fu_api.models.custom_user_model import CustomUser


def assign_profile_images(apps, schema_editor):
    male_dir = os.path.join(settings.MEDIA_ROOT, "male")
    female_dir = os.path.join(settings.MEDIA_ROOT, "female")

    if not os.path.isdir(male_dir) or not os.path.isdir(female_dir):
        return

    male_images = sorted(
        [
            fname
            for fname in os.listdir(male_dir)
            if os.path.isfile(os.path.join(male_dir, fname))
        ]
    )
    female_images = sorted(
        [
            fname
            for fname in os.listdir(female_dir)
            if os.path.isfile(os.path.join(female_dir, fname))
        ]
    )

    male_qs = CustomUser.objects.filter(sex_id=0).order_by("id")
    female_qs = CustomUser.objects.filter(sex_id=1).order_by("id")

    for user, filename in zip(male_qs, male_images):
        user.profile_image = os.path.join("male", filename)
        user.save(update_fields=["profile_image"])

    for user, filename in zip(female_qs, female_images):
        user.profile_image = os.path.join("female", filename)
        user.save(update_fields=["profile_image"])


def unassign_profile_images(apps, schema_editor):
    CustomUser.objects.filter(profile_image__isnull=False).update(profile_image=None)


class Migration(migrations.Migration):

    dependencies = [
        ("fu_api", "0002_populate_db_with_test_users"),
    ]

    operations = [
        migrations.RunPython(
            assign_profile_images, reverse_code=unassign_profile_images
        ),
    ]
