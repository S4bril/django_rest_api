from django.core.management.base import BaseCommand
from fu_api.matching_models.binary_classification.match_model import MatchModel


class Command(BaseCommand):
    def handle(self, *args, **options):
        model = MatchModel("feature_vectors.csv")
        model.train()

        model.evaluate()

        model.cross_validate()

        model.save("match_model.xgb")
