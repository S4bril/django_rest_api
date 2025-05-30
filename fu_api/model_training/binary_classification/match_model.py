import numpy as np
import pandas as pd
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from fu_api.model_training.binary_classification.feature_store import FeatureStore


class MatchModel:
    def __init__(
        self, feature_file: str, test_size: float = 0.2, random_state: int = 42
    ):
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
            stratify=self.y,
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

        scores = cross_val_score(self.model, self.X, self.y, cv=cv, scoring="accuracy")
        print(f"Cross-Validation Results ({cv} folds):")
        print(f"Mean Accuracy: {scores.mean():.4f}")
        print(f"Std Deviation: {scores.std():.4f}")

    def save(self, path: str):
        self.model.save_model(path)

    def load(self, path: str):
        self.model.load_model(path)
