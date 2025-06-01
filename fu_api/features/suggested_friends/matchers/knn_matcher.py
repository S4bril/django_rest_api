from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from fu_api.features.suggested_friends.matchers.vector_engineer import (
    IndividualFeatureEngineer,
)

from .base import BaseMatcher

NUMBER_OF_VALIDATED_USERS = 100
NUMBER_OF_OUTPUT_USERS = 100


class KNNMatcher(BaseMatcher):
    def __init__(self, features=None):
        self.feature_engineer = IndividualFeatureEngineer()
        self.scaler = StandardScaler()

    def compute_feature_vector(self, user):
        return self.feature_engineer.get_feature_vector(user)

    def get_matches(self, user):
        candidates = self.get_valid_candidates(user, NUMBER_OF_VALIDATED_USERS)
        if not candidates:
            return []

        candidate_vectors = [self.compute_feature_vector(c) for c in candidates]
        user_vector = self.compute_feature_vector(user)

        scaled_vectors = self.scaler.fit_transform(candidate_vectors + [user_vector])
        user_scaled = scaled_vectors[-1].reshape(1, -1)
        candidates_scaled = scaled_vectors[:-1]

        knn = NearestNeighbors(n_neighbors=NUMBER_OF_OUTPUT_USERS, metric="euclidean")
        knn.fit(candidates_scaled)
        _, indices = knn.kneighbors(user_scaled)

        return [candidates[int(i)] for i in indices[0]]
