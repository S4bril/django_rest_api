from datetime import datetime
import numpy as np
from typing import List, Dict, Optional
from geopy.distance import great_circle
from sentence_transformers import SentenceTransformer
# from xgboost import XGBClassifier
# import openai


class User:
    def __init__(self, data: Dict):
        self.id = data['username']
        self.bio = data['bio']
        self.passions = set(data['passions'])
        self.location = tuple(data['location'])
        self.birthdate = datetime.strptime(data['birthday'], "%Y-%m-%d").date()

    @property
    def age(self):
        today = datetime.now().date()
        return today.year - self.birthdate.year - (
            (today.month, today.day) < 
            (self.birthdate.month, self.birthdate.day)
        )

    @property
    def bio_embedding(self):
        if 'bio' not in self._embeddings:
            self._embeddings['bio'] = SentenceTransformer(
                'paraphrase-multilingual-MiniLM-L12-v2'
            ).encode(self.bio)
        return self._embeddings['bio']


class UserPair:
    def __init__(self, user_a: User, user_b: User):
        self.user_a = user_a
        self.user_b = user_b
        self.features: Optional[np.ndarray] = None
        self.label: Optional[float] = None

    @property
    def key(self):
        return tuple(sorted([self.user_a.id, self.user_b.id]))


class PairGenerator:
    def __init__(self, users: List[User]):
        self.users = users

    def generate_pairs(
        self,
        max_age_diff: int = 5,
        min_common_passions: int = 1,
        max_distance_km: float = 50.0
    ) -> List[UserPair]:
        pairs = []

        for i in range(len(self.users)):
            user_a = self.users[i]
            for j in range(i+1, len(self.users)):
                user_b = self.users[j]

                if abs(user_a.age - user_b.age) > max_age_diff:
                    continue

                common = len(user_a.passions & user_b.passions)
                if common < min_common_passions:
                    continue
                distance = great_circle(
                    user_a.location, 
                    user_b.location
                ).kilometers
                if distance > max_distance_km:
                    continue

                pairs.append(UserPair(user_a, user_b))

        return pairs


# class APILabeler:
#     def __init__(self, api_key: str):
#         openai.api_key = api_key
#         self.prompt_template = """Rate compatibility (0 or 1) for these two profiles:

#         User A:
#         Bio: {bio_a}
#         Passions: {passions_a}

#         User B:
#         Bio: {bio_b}
#         Passions: {passions_b}

#         Answer ONLY with 0 (no match) or 1 (good match). 
#         Consider shared interests, bio compatibility, and potential connection."""

#     def label_pair(self, pair: UserPair) -> float:
#         response = openai.chat.completions.create(
#             model="gpt-4o",
#             messages=[{
#                 "role": "user",
#                 "content": self.prompt_template.format(
#                     bio_a=pair.user_a.bio,
#                     passions_a=", ".join(map(str, pair.user_a.passions)),
#                     bio_b=pair.user_b.bio,
#                     passions_b=", ".join(map(str, pair.user_b.passions))
#                 )
#             }],
#             temperature=0.1,
#             max_tokens=1
#         )
#         return float(response.choices[0].message.content.strip())


# class MatchModel:
#     def __init__(self):
#         self.model = XGBClassifier()
#         self.bio_encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

#     def extract_features(self, pair: UserPair) -> np.ndarray:
#         """Feature engineering pipeline"""
#         # Passion compatibility
#         common = len(pair.user_a.passions & pair.user_b.passions)
#         total = len(pair.user_a.passions | pair.user_b.passions)
#         jaccard = common / total if total > 0 else 0

#         # Location proximity
#         distance = great_circle(pair.user_a.location, pair.user_b.location).km

#         # Bio similarity
#         emb_a = pair.user_a.bio_embedding
#         emb_b = pair.user_b.bio_embedding
#         cosine_sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))

#         return np.array([jaccard, distance, cosine_sim])

#     def train(self, pairs: List[UserPair]):
#         X = np.array([self.extract_features(p) for p in pairs])
#         y = np.array([p.label for p in pairs])
#         self.model.fit(X, y)

#     def predict(self, pair: UserPair) -> float:
#         return self.model.predict_proba(self.extract_features(pair))[0][1]

#     def save(self, path: str):
#         self.model.save_model(path)

#     def load(self, path: str):
#         self.model.load_model(path)

# if __name__ == "__main__":
#     users = [User(data) for data in load_users_from_csv(r"fu_api\matching_models\binary_classification\data\users_dataset.csv")]

#     generator = PairGenerator(users)
#     pairs = generator.generate_pairs(
#         strategy='combined',
#         max_km=100,
#         min_common=1
#     )

#     # 3. Label pairs using GPT-4o
#     labeler = APILabeler("your-api-key")
#     for pair in pairs:
#         pair.label = labeler.label_pair(pair)

#     # 4. Train model
#     model = MatchModel()
#     model.train(pairs)

#     # 5. Save model
#     model.save("match_model.xgb")
