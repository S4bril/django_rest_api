import numpy as np
import random
from typing import List, Dict, Optional
from geopy.distance import great_circle
from fu_api.helpers.load_users import load_users_from_json
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import BallTree
from xgboost import XGBClassifier
import openai
from collections import defaultdict

class User:
    def __init__(self, user_data: Dict):
        self.id = user_data['username']
        self.bio = user_data['bio']
        self.passions = set(user_data['passions'])
        self.location = tuple(user_data['location'])
        self._embeddings = {}
        
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
        self._build_indices()
        
    def _build_indices(self):
        """Precompute data structures for efficient pairing"""
        # Geospatial index
        locations = np.array([u.location for u in self.users])
        self.location_tree = BallTree(np.radians(locations), metric='haversine')
        
        # Passion index
        self.passion_index = defaultdict(set)
        for idx, user in enumerate(self.users):
            for p in user.passions:
                self.passion_index[p].add(idx)
                
    def generate_pairs(self, strategy: str = 'combined', **params) -> List[UserPair]:
        """
        Generate pairs using specified strategy
        Available strategies:
        - 'random': Simple random sampling
        - 'location': Within geographic radius
        - 'passion': Shared interest matching
        - 'combined': Location + passion filtering
        """
        if strategy == 'random':
            return self._random_pairs(**params)
        elif strategy == 'location':
            return self._location_pairs(**params)
        elif strategy == 'passion':
            return self._passion_pairs(**params)
        elif strategy == 'combined':
            return self._combined_pairs(**params)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _random_pairs(self, sample_size: int = 1000) -> List[UserPair]:
        """Random sampling with deduplication"""
        pairs = set()
        while len(pairs) < sample_size:
            a, b = random.sample(self.users, 2)
            pair = UserPair(a, b)
            pairs.add(pair.key)
        return [UserPair(*pair) for pair in pairs]
    
    def _location_pairs(self, max_km: float = 50) -> List[UserPair]:
        """Find all pairs within geographic radius"""
        pairs = []
        earth_radius_km = 6371
        
        for i, user in enumerate(self.users):
            # Query radius in radians
            radius = max_km / earth_radius_km
            indices = self.location_tree.query_radius(
                np.radians([user.location]), 
                r=radius
            )[0]
            
            for j in indices:
                if i < j:  # Avoid duplicates
                    pairs.append(UserPair(user, self.users[j]))
                    
        return pairs
    
    def _passion_pairs(self, min_common: int = 2) -> List[UserPair]:
        """Match users sharing minimum common passions"""
        pairs = []
        seen = set()
        
        for passion, user_indices in self.passion_index.items():
            if len(user_indices) < 2:
                continue
                
            # Get all combinations for this passion
            users = [self.users[i] for i in user_indices]
            for i in range(len(users)):
                for j in range(i+1, len(users)):
                    pair = UserPair(users[i], users[j])
                    if len(users[i].passions & users[j].passions) >= min_common:
                        if pair.key not in seen:
                            pairs.append(pair)
                            seen.add(pair.key)
        return pairs
    
    def _combined_pairs(self, max_km: float = 50, min_common: int = 1) -> List[UserPair]:
        """Hybrid approach: location first, then passion"""
        location_pairs = self._location_pairs(max_km)
        return [
            p for p in location_pairs
            if len(p.user_a.passions & p.user_b.passions) >= min_common
        ]

class APILabeler:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.prompt_template = """Rate compatibility (0 or 1) for these two profiles:
        
        User A:
        Bio: {bio_a}
        Passions: {passions_a}
        
        User B:
        Bio: {bio_b}
        Passions: {passions_b}
        
        Answer ONLY with 0 (no match) or 1 (good match). 
        Consider shared interests, bio compatibility, and potential connection."""
        
    def label_pair(self, pair: UserPair) -> float:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": self.prompt_template.format(
                    bio_a=pair.user_a.bio,
                    passions_a=", ".join(map(str, pair.user_a.passions)),
                    bio_b=pair.user_b.bio,
                    passions_b=", ".join(map(str, pair.user_b.passions))
                )
            }],
            temperature=0.1,
            max_tokens=1
        )
        return float(response.choices[0].message.content.strip())

class MatchModel:
    def __init__(self):
        self.model = XGBClassifier()
        self.bio_encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def extract_features(self, pair: UserPair) -> np.ndarray:
        """Feature engineering pipeline"""
        # Passion compatibility
        common = len(pair.user_a.passions & pair.user_b.passions)
        total = len(pair.user_a.passions | pair.user_b.passions)
        jaccard = common / total if total > 0 else 0
        
        # Location proximity
        distance = great_circle(pair.user_a.location, pair.user_b.location).km
        
        # Bio similarity
        emb_a = pair.user_a.bio_embedding
        emb_b = pair.user_b.bio_embedding
        cosine_sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))
        
        return np.array([jaccard, distance, cosine_sim])
    
    def train(self, pairs: List[UserPair]):
        X = np.array([self.extract_features(p) for p in pairs])
        y = np.array([p.label for p in pairs])
        self.model.fit(X, y)
        
    def predict(self, pair: UserPair) -> float:
        return self.model.predict_proba(self.extract_features(pair))[0][1]
    
    def save(self, path: str):
        self.model.save_model(path)
        
    def load(self, path: str):
        self.model.load_model(path)

# Example usage
if __name__ == "__main__":
    # 1. Load user data
    users = [User(data) for data in load_users_from_json()]
    
    # 2. Generate candidate pairs
    generator = PairGenerator(users)
    pairs = generator.generate_pairs(
        strategy='combined',
        max_km=100,
        min_common=1
    )
    
    # 3. Label pairs using GPT-4o
    labeler = APILabeler("your-api-key")
    for pair in pairs:
        pair.label = labeler.label_pair(pair)
    
    # 4. Train model
    model = MatchModel()
    model.train(pairs)
    
    # 5. Save model
    model.save("match_model.xgb")