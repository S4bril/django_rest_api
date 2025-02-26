import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from fu_api.models import CustomUser

def compute_data_vector(user):
    data_vector = 30 * [0]
    passions = user.passions
    for passion in passions:
        data_vector[passion - 1] = 1
    return data_vector

if __name__ == "__main__":
    users = CustomUser.objects.all()
    for user in users:
        user.data_vector = compute_data_vector(user)
        user.save()
