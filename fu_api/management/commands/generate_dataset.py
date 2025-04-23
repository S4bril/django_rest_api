from django.core.management.base import BaseCommand
from tqdm import tqdm
from fu_api.helpers.load_users import load_users_from_csv
from fu_api.matching_models.binary_classification.pairs_generator import APILabeler, FeatureStore, PairFactory, User

import random

USERS_DATASET = r"fu_api\matching_models\binary_classification\data\users_dataset.csv"


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = [User(data) for data in load_users_from_csv(USERS_DATASET)]

        generator = PairFactory(users)

        pairs = generator.generate_pairs(
            max_age_diff=100000,
            min_common_passions=0,
            max_distance_km=10000000
        )

        print("Number of pairs: ", len(pairs))

        labeler = APILabeler(api_key="")#"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")
        #10767
        for pair in tqdm(pairs):
            if labeler.label_pair(pair) is not None:
                pair.calculate_features()
                FeatureStore.save_to_csv([pair], "feature_vectors.csv")
