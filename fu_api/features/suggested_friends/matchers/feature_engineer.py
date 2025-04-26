from datetime import date
from geopy.distance import great_circle
from sentence_transformers import SentenceTransformer
import numpy as np

DEFAULT_FEATURES = ['jaccard', 'distance', 'age_diff', 'bio_similarity']


class FeatureEngineer:
    def __init__(self, enabled_features=None):
        self.enabled_features = enabled_features or DEFAULT_FEATURES
        self.bio_encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        self.available_features = {
            'jaccard': self.compute_jaccard,
            'distance': self.compute_distance,
            'age_diff': self.compute_age_diff,
            'bio_similarity': self.compute_bio_similarity,
        }
        for feature in self.enabled_features:
            if feature not in self.available_features:
                raise ValueError(f"Invalid feature: {feature}. Available features: {list(self.available_features.keys())}")

    def compute_jaccard(self, user, candidate):
        passions1 = set(user.passions)
        passions2 = set(candidate.passions)
        if not passions1 and not passions2:
            return 0
        return len(passions1 & passions2) / len(passions1 | passions2)

    def compute_distance(self, user, candidate):
        if not user.location or not candidate.location:
            return 1000
        return great_circle(
            (user.location.latitude, user.location.longitude),
            (candidate.location.latitude, candidate.location.longitude)
        ).kilometers

    def compute_age_diff(self, user, candidate):
        def calculate_age(birthdate):
            today = date.today()
            return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return abs(calculate_age(user.birthday) - calculate_age(candidate.birthday))

    def compute_bio_similarity(self, user, candidate):
        bio1 = user.bio or ""
        bio2 = candidate.bio or ""
        emb1 = self.bio_encoder.encode(bio1)
        emb2 = self.bio_encoder.encode(bio2)
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def get_feature_vector(self, user, candidate):
        features = []
        for feature in self.enabled_features:
            features.append(self.available_features[feature](user, candidate))
        return features
