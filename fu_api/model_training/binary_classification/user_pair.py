from typing import Optional

import numpy as np
from geopy.distance import great_circle

from fu_api.model_training.binary_classification.user import User


class UserPair:
    def __init__(self, user_a: User, user_b: User):
        self.user_a = user_a
        self.user_b = user_b
        self.features: Optional[np.ndarray] = None
        self.label: Optional[float] = None

    def calculate_features(self):
        common = len(self.user_a_ids & self.user_b.passions_ids)
        total = len(self.user_a.passions_ids | self.user_b.passions_ids)
        jaccard = common / total if total > 0 else 0

        age_diff = abs(self.user_a.age - self.user_b.age)

        emb_a = self.user_a.bio_embedding
        emb_b = self.user_b.bio_embedding
        cosine_sim = np.dot(emb_a, emb_b) / (
            np.linalg.norm(emb_a) * np.linalg.norm(emb_b)
        )

        self.features = np.array([jaccard, self.distance, age_diff, cosine_sim])

    @property
    def distance(self):
        return round(
            great_circle(self.user_a.location, self.user_b.location).kilometers, 2
        )
