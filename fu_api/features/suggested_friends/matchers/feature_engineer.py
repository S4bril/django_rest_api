from datetime import date
import numpy as np

DEFAULT_FEATURES = ['jaccard', 'distance', 'age_diff', 'bio_similarity']


class FeatureEngineer:
    def __init__(self, enabled_features=None):
        self.enabled_features = enabled_features or DEFAULT_FEATURES

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
        passions1 = set(user.passions_ids)
        passions2 = set(candidate.passions_ids)
        if not passions1 and not passions2:
            return 0
        return len(passions1 & passions2) / len(passions1 | passions2)

    def compute_distance(self, user, candidate):
        if not user.location or not candidate.location:
            return None

        return self._haversine(
            user.location.latitude,
            user.location.longitude,
            candidate.location.latitude,
            candidate.location.longitude
        )

    def compute_age_diff(self, user, candidate):
        def calculate_age(birthdate):
            today = date.today()
            return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return abs(calculate_age(user.birthday) - calculate_age(candidate.birthday))

    def compute_bio_similarity(self, user, candidate):
        emb1 = user.bio_embedding
        emb2 = candidate.bio_embedding
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def get_feature_vector(self, user, candidate):
        features = []
        for feature in self.enabled_features:
            features.append(self.available_features[feature](user, candidate))
        return features

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0

        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        lat1 = np.radians(lat1)
        lat2 = np.radians(lat2)

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.atan2(np.sqrt(a), np.sqrt(1 - a))

        return R * c
