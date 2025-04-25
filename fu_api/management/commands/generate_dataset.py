from tqdm import tqdm
from django.core.management.base import BaseCommand
from fu_api.helpers.load_users import load_users_from_csv
from fu_api.matching_models.binary_classification.api_labeler import APILabeler
from fu_api.matching_models.binary_classification.feature_store import FeatureStore
from fu_api.matching_models.binary_classification.pair_factory import PairFactory
from fu_api.matching_models.binary_classification.user import User


USERS_DATASET = r"fu_api\matching_models\binary_classification\data\users_dataset.csv"


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = [User(data) for data in load_users_from_csv(USERS_DATASET)]

        generator = PairFactory(users)

        pairs = generator.generate_pairs(
            max_age_diff=10,
            min_common_passions=1,
            max_distance_km=100
        )

        print("Number of pairs: ", len(pairs))

        labeler = APILabeler(api_key="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")
        for pair in tqdm(pairs):
            labeler.label_pair(pair)
            pair.calculate_features()
            FeatureStore.save_to_csv([pair], "feature_vectors.csv")
