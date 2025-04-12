from django.core.management.base import BaseCommand
from fu_api.helpers.load_users import load_users_from_csv
from fu_api.matching_models.binary_classification.pairs_generator import PairGenerator, User

USERS_DATASET = r"fu_api\matching_models\binary_classification\data\users_dataset.csv"


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = [User(data) for data in load_users_from_csv(USERS_DATASET)]

        generator = PairGenerator(users)

        pairs = generator.generate_pairs(
            max_age_diff=10,
            min_common_passions=1,
            max_distance_km=100
        )

        print("Number of pairs: ", len(pairs))
