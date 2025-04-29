import numpy as np
import pandas as pd
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from fu_api.matching_model.binary_classification.feature_store import FeatureStore


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

    def evaluate(self):
        y_pred = self.predict()

        print("\nConfusion Matrix:")
        print(confusion_matrix(self.y_test, y_pred))
        print(f"Accuracy: {accuracy_score(self.y_test, y_pred):.4f}")

    def save(self, path: str):
        self.model.save_model(path)

    def load(self, path: str):
        self.model.load_model(path)
