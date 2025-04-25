import numpy as np
import xgboost as xgb
from datetime import date
from geopy.distance import great_circle
from sentence_transformers import SentenceTransformer
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from .base import BaseMatcher

FEATURE_NAMES = ["jaccard", "distance", "age_diff", "bio_similarity"]

NUMBER_OF_VALIDATED_USERS = 50
NUMBER_OF_OUTPUT_USERS = 10

class XGBMatcher(BaseMatcher):
    def __init__(self, model_path="match_model.xgb"):
        self.model = xgb.Booster()
        self.model.load_model(model_path)
        self.bio_encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def compute_feature_vector(self, user, candidate):
        passions1 = set(user.passions)
        passions2 = set(candidate.passions)
        jaccard = len(passions1 & passions2) / len(passions1 | passions2) if passions1 or passions2 else 0

        if user.location and candidate.location:
            distance = great_circle(
                (user.location.latitude, user.location.longitude),
                (candidate.location.latitude, candidate.location.longitude)
            ).kilometers
        else:
            distance = 1000

        age_diff = abs(self.calculate_age(user.birthday) - self.calculate_age(candidate.birthday))

        bio_sim = self.compute_bio_similarity(user.bio, candidate.bio)
        return [jaccard, distance, age_diff, bio_sim]

    def calculate_age(self, birthdate):
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    def compute_bio_similarity(self, bio1, bio2):
        emb1 = self.bio_encoder.encode(bio1 or "")
        emb2 = self.bio_encoder.encode(bio2 or "")
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    def serialize_matches(self, matches):
        return FriendSerializer(matches, many=True)

    def get_matches(self, user):
        candidates = self.get_valid_candidates(user, NUMBER_OF_VALIDATED_USERS)
        features = []
        valid_candidates = []
        for candidate in candidates:
            try:
                feature_vector = self.compute_feature_vector(user, candidate)
                features.append(feature_vector)
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
            candidate_serialized = FriendSerializer(candidate).data
            candidate_serialized["match_probability"] = float(probabilities[idx])
            serialized_matches.append(candidate_serialized)
        return serialized_matches
