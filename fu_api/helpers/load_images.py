import os
import sys
import django
from django.core.files import File

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fu_api.models.custom_user_model import CustomUser

def assign_default_profile_image():
    default_image_man_path = 'media/profile_images/default_man_1.jpg'
    default_image_woman_path = 'media/profile_images/default_woman_1.jpg'

    for user in CustomUser.objects.all():
        if not user.profile_image:
            image_path = default_image_man_path if user.sex == 0 else default_image_woman_path

            with open(image_path, 'rb') as image_file:
                django_file = File(image_file)
                user.profile_image.save(image_path.split('/')[-1], django_file, save=True)
                print(f"Assigned default image to {user.username}")

if __name__ == "__main__":
    assign_default_profile_image()
