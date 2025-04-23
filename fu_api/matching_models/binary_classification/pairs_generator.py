import csv
from datetime import datetime
import json
import os
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from geopy.distance import great_circle
from sentence_transformers import SentenceTransformer
from sklearn.metrics import accuracy_score, average_precision_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import openai
from imblearn.under_sampling import RandomUnderSampler

from config import settings


class User:
    def __init__(self, data: Dict):
        self.id = data['email']
        self.bio = data['bio']
        self.passions = set(data['passions'])
        self.location = tuple(data['location'])
        self.birthdate = datetime.strptime(data['birthday'], "%Y-%m-%d").date()
        self._embeddings = {}

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

    def calculate_features(self):
        common = len(self.user_a.passions & self.user_b.passions)
        total = len(self.user_a.passions | self.user_b.passions)
        jaccard = common / total if total > 0 else 0

        age_diff = abs(self.user_a.age - self.user_b.age)

        emb_a = self.user_a.bio_embedding
        emb_b = self.user_b.bio_embedding
        cosine_sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))

        self.features = np.array([jaccard, self.distance, age_diff, cosine_sim])

    @property
    def distance(self):
        return round(great_circle(
            self.user_a.location, 
            self.user_b.location
        ).kilometers, 2)


class PairFactory:
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


class APILabeler:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.prompt_template = """Rate compatibility (0 or 1) for these two profiles:

        User A:
        Bio: {bio_a}
        Passions: {passions_a}
        Age: {age_a}

        User B:
        Bio: {bio_b}
        Passions: {passions_b}
        Age: {age_b}

        Distance between users: {distance} km

        Answer ONLY with 0 (no match) or 1 (good match). 
        Consider shared interests, bio compatibility, age difference, distance separating users and potential connection."""

    def label_pair(self, pair: UserPair) -> float:
        if pair.distance >= 100.0 or abs(pair.user_a.age - pair.user_b.age) >= 10 or len(pair.user_a.passions & pair.user_b.passions) == 0:
            pair.label = 0.0
            return 0.0
        return None
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": self.prompt_template.format(
                    bio_a=pair.user_a.bio,
                    passions_a=", ".join(self._extract_passions_names(pair.user_a.passions)),
                    age_a=pair.user_a.age,
                    bio_b=pair.user_b.bio,
                    passions_b=", ".join(self._extract_passions_names(pair.user_b.passions)),
                    age_b=pair.user_b.age,
                    distance=pair.distance
                )
            }],
            temperature=0.4,
            logit_bias={
                "0": 20,
                "1": 20
            },
            max_tokens=1
        )
        pair.label = float(response.choices[0].message.content.strip())
        return pair.label

    def _extract_passions_names(self, passions_ids):
        passions_file_path = os.path.join(settings.BASE_DIR, "fu_api", "json_forms", "passions.json")
        with open(passions_file_path, 'r', encoding="utf-8") as file:
            passions = json.load(file)['passions']
            return [passions.get(str(p_id), {}).get('name', 'Unknown') for p_id in passions_ids]


class FeatureStore:
    CSV_HEADER = ['jaccard', 'distance', 'age_diff', 'bio_similarity', 'label']

    @staticmethod
    def save_to_csv(pairs: List[UserPair], filename: str):
        file_exists = os.path.exists(filename)
        write_header = not file_exists or os.stat(filename).st_size == 0

        with open(filename, 'a' if file_exists else 'w', newline='') as f:
            writer = csv.writer(f)
            
            if write_header:
                writer.writerow(FeatureStore.CSV_HEADER)

            for pair in pairs:
                if pair.features is None:
                    pair.calculate_features()
                    
                writer.writerow([
                    pair.features[0],  # jaccard
                    pair.features[1],  # distance
                    pair.features[2],  # age difference
                    pair.features[3],  # bio similarity
                    pair.label
                ])

    @staticmethod
    def load_from_csv(filename: str) -> Tuple[np.ndarray, np.ndarray]:
        data = np.loadtxt(filename, delimiter=',', skiprows=1)
        X = data[:, :-1]
        y = data[:, -1]
        return X, y


class MatchModel:
    def __init__(self, feature_file: str, test_size: float = 0.2, random_state: int = 42):
        self.model = XGBClassifier()
        
        data = pd.read_csv(feature_file)
        
        feature_columns = FeatureStore.CSV_HEADER[:-1]
        target_column = FeatureStore.CSV_HEADER[-1]
        
        X = data[feature_columns]
        y = data[target_column]
        
        undersampler = RandomUnderSampler(random_state=random_state)
        self.X, self.y = undersampler.fit_resample(X, y)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, 
            self.y,
            test_size=test_size,
            random_state=random_state,
            stratify=self.y
        )

    def train(self):
        self.model.fit(self.X, self.y)

    def predict(self, X: np.ndarray = None) -> float:
        if X is None:
            X = self.X_test
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray = None) -> np.ndarray:
        if X is None:
            X = self.X_test
        return self.model.predict_proba(X)
    
    def evaluate(self):
        y_pred = self.predict()
        y_proba = self.predict_proba()[:, 1]

        print("Classification Report:")
        print(classification_report(self.y_test, y_pred))

        print("\nConfusion Matrix:")
        print(confusion_matrix(self.y_test, y_pred))

        print("\nKey Metrics:")
        print(f"Accuracy: {accuracy_score(self.y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(self.y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(self.y_test, y_pred):.4f}")
        print(f"F1 Score: {f1_score(self.y_test, y_pred):.4f}")

        print(f"\nROC AUC: {roc_auc_score(self.y_test, y_proba):.4f}")
        print(f"Average Precision: {average_precision_score(self.y_test, y_proba):.4f}")

    def cross_validate(self, cv: int = 5):
        """Perform cross-validation"""
        from sklearn.model_selection import cross_val_score
        scores = cross_val_score(
            self.model,
            self.X,
            self.y,
            cv=cv,
            scoring='accuracy'
        )
        print(f"Cross-Validation Results ({cv} folds):")
        print(f"Mean Accuracy: {scores.mean():.4f}")
        print(f"Std Deviation: {scores.std():.4f}")

    def save(self, path: str):
        self.model.save_model(path)

    def load(self, path: str):
        self.model.load_model(path)
