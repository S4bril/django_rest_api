from datetime import date

import numpy as np


class IndividualFeatureEngineer:
    def __init__(self):
        self.features = {
            "passions_vector": self.compute_passions_vector,
            "location_coords": self.compute_location_coords,
            "age": self.compute_age,
            "bio_embedding": self.compute_bio_embedding,
            "friend_count": self.compute_friend_count,
        }

    def compute_passions_vector(self, user):
        passions_vector = [0] * 50
        for p_id in user.passions_ids:
            if 0 <= p_id < 50:
                passions_vector[p_id] = 1
        return passions_vector

    def compute_location_coords(self, user):
        if user.location:
            return [user.location.latitude, user.location.longitude]
        return [0.0, 0.0]

    def compute_age(self, user):
        today = date.today()
        return [
            today.year
            - user.birthday.year
            - ((today.month, today.day) < (user.birthday.month, user.birthday.day))
        ]

    def compute_bio_embedding(self, user):
        return user.bio_embedding

    def compute_friend_count(self, user):
        return [user.friends.count()]

    def get_feature_vector(self, user):
        vector = []
        for feature in self.features:
            vector.extend(self.features[feature](user))
        return np.array(vector)
