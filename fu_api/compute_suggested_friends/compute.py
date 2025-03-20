import os
import sys
import django

from sklearn.neighbors import NearestNeighbors
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'foundyou_api')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from fu_api.models import CustomUser

NUMBER_OF_POTENTIAL_FRIENDS = 70
NUMBER_OF_OTPUT_USERS = 10

def get_valid_potential_friends_from_db(user):
    try:
        excluded_users = user.friends.all() | user.blocked_users.all() | CustomUser.objects.filter(id=user.id)
        suggested_users = (
            CustomUser.objects.exclude(id__in=excluded_users.values_list('id', flat=True))
            [:NUMBER_OF_POTENTIAL_FRIENDS]
        )
        return suggested_users
    except Exception as e:
        print(f"Error fetching suggested users: {e}")
        return CustomUser.objects.none()

def compute_data_vector(user):
    data_vector = 30 * [0]
    passions = user.passions
    for passion in passions:
        data_vector[passion - 1] = 1
    return data_vector

def get_suggested_friends(user):
    potential_friends = get_valid_potential_friends_from_db(user)
    
    if not potential_friends:
        return []

    friend_vectors = np.array([compute_data_vector(friend) for friend in potential_friends])
    
    user_vector = np.array(compute_data_vector(user)).reshape(1, -1)
    
    knn = NearestNeighbors(n_neighbors=NUMBER_OF_OTPUT_USERS, metric="cosine")
    knn.fit(friend_vectors)

    _, indices = knn.kneighbors(user_vector)
    
    top_friends = [potential_friends[int(i)] for i in indices[0]]

    return top_friends