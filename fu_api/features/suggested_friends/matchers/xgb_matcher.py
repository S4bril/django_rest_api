import numpy as np
import xgboost as xgb

from fu_api.features.suggested_friends.matchers.feature_engineer import FeatureEngineer
from fu_api.features.suggested_friends.serializers import FriendSerializer

from .base import BaseMatcher

FEATURE_NAMES = ["jaccard", "distance", "age_diff", "bio_similarity"]
NUMBER_OF_VALIDATED_USERS = 50
NUMBER_OF_OUTPUT_USERS = 10


class XGBMatcher(BaseMatcher):
    def __init__(self, features=None, model_path="match_model.xgb"):
        self.feature_engineer = FeatureEngineer(features)
        self.model = xgb.Booster()
        self.model.load_model(model_path)

    def compute_feature_vector(self, user, candidate):
        return self.feature_engineer.get_feature_vector(user, candidate)

    def get_matches(self, user):
        candidates = self.get_valid_candidates(user, NUMBER_OF_VALIDATED_USERS)
        features = []
        valid_candidates = []

        for candidate in candidates:
            try:
                features.append(self.compute_feature_vector(user, candidate))
                valid_candidates.append(candidate)
            except Exception as e:
                print(f"Skipping candidate {candidate.id}: {e}")
                continue

        if not features:
            return []

        dmatrix = xgb.DMatrix(np.array(features), feature_names=FEATURE_NAMES)
        probabilities = self.model.predict(dmatrix)
        sorted_indices = np.argsort(probabilities)[::-1]
        serialized_matches = []
        for idx in sorted_indices[:NUMBER_OF_OUTPUT_USERS]:
            candidate = valid_candidates[idx]
            candidate_serialized = FriendSerializer(
                candidate, context={"current_user": user}
            ).data
            candidate_serialized["match_probability"] = float(probabilities[idx])
            serialized_matches.append(candidate_serialized)
        return serialized_matches
