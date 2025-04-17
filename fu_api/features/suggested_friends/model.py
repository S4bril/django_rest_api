from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from geopy.distance import great_circle
from sentence_transformers import SentenceTransformer
import numpy as np
import xgboost as xgb
import os

from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.models.custom_user_model import CustomUser

class MatchRecommendationView(APIView):
    bio_encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    model = xgb.Booster()
    model_path = "match_model.xgb"
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if os.path.exists(self.model_path):
            self.model.load_model(self.model_path)
        else:
            return Response({"error": "Model not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        current_user = request.user
        if not current_user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        candidates = self.get_valid_candidates(current_user)
        if not candidates:
            return Response({"message": "No potential matches found"}, status=status.HTTP_200_OK)

        features = []
        valid_candidates = []
        for candidate in candidates:
            try:
                feature_vector = self.create_feature_vector(current_user, candidate)
                features.append(feature_vector)
                valid_candidates.append(candidate)
            except Exception as e:
                print(f"Skipping candidate {candidate.id}: {str(e)}")
                continue

        if not features:
            return Response({"message": "No valid matches found"}, status=status.HTTP_200_OK)

        dmatrix = xgb.DMatrix(np.array(features))
        probabilities = self.model.predict(dmatrix)

        sorted_indices = np.argsort(probabilities)[::-1][:10]
        results = []
        for idx in sorted_indices:
            results.append({
                "user": self.serialize_user(valid_candidates[idx]),
                "match_probability": float(probabilities[idx])
            })

        return Response({"results": results})

    def get_valid_candidates(self, user):
        excluded = Q(id=user.id) | Q(friends=user) | Q(rejected_users=user)
        return CustomUser.objects.exclude(excluded).select_related('location')#[:100]  # Limit for performance

    def create_feature_vector(self, user1, user2):
        passions1 = set(user1.passions)
        passions2 = set(user2.passions)
        jaccard = len(passions1 & passions2) / len(passions1 | passions2) if passions1 or passions2 else 0

        distance = self.calculate_distance(user1.location, user2.location)

        age_diff = abs(self.calculate_age(user1.birthday) - self.calculate_age(user2.birthday))

        bio_sim = self.calculate_bio_similarity(user1.bio, user2.bio)

        return [jaccard, distance, age_diff, bio_sim]

    def calculate_distance(self, loc1, loc2):
        if not loc1 or not loc2:
            return 1000
        return great_circle(
            (loc1.latitude, loc1.longitude),
            (loc2.latitude, loc2.longitude)
        ).kilometers

    def calculate_bio_similarity(self, bio1, bio2):
        emb1 = self.bio_encoder.encode(bio1 or "")
        emb2 = self.bio_encoder.encode(bio2 or "")
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def serialize_user(self, user):
        serializer = FriendSerializer(
            user,
            context={'request': self.request}
        )
        data = serializer.data
        return data

    def calculate_age(self, birthdate):
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    def serialize_location(self, location):
        if not location:
            return None
        return {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "updated_at": location.updated_at
        }
