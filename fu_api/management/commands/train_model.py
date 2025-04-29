from django.core.management.base import BaseCommand
from fu_api.matching_model.binary_classification.match_model import MatchModel


class Command(BaseCommand):
    def handle(self, *args, **options):
        model = MatchModel("feature_vectors.csv")
        model.train()
        model.evaluate()
        model.save("match_model.xgb")
