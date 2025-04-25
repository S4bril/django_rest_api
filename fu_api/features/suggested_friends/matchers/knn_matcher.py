import numpy as np
from sklearn.neighbors import NearestNeighbors
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from .base import BaseMatcher

NUMBER_OF_VALIDATED_USERS = 100
NUMBER_OF_OUTPUT_USERS = 100

class KNNMatcher(BaseMatcher):

    def compute_feature_vector(self, user, candidate):
        data_vector = [0] * 30
        for passion in candidate.passions:
            data_vector[passion - 1] = 1
        return data_vector

    def get_matches(self, user):
        candidates = self.get_valid_candidates(user, NUMBER_OF_VALIDATED_USERS)
        if not candidates:
            return []

        candidate_vectors = [self.compute_feature_vector(user, candidate) for candidate in candidates]
        user_vector = np.array(self.compute_feature_vector(user, user)).reshape(1, -1)

        candidate_vectors = np.array(candidate_vectors)
        knn = NearestNeighbors(n_neighbors=NUMBER_OF_OUTPUT_USERS, metric="cosine")
        knn.fit(candidate_vectors)
        _, indices = knn.kneighbors(user_vector)
        serialized_candidates = FriendSerializer([candidates[int(i)] for i in indices[0]], many=True)
        return serialized_candidates.data
