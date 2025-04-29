import numpy as np
import csv
import os
from typing import List, Tuple
from fu_api.matching_model.binary_classification.user_pair import UserPair


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
