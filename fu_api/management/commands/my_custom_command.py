from django.core.management.base import BaseCommand
from fu_api.matching_models.binary_classification.pairs_generator import PairsGenerator


class Command(BaseCommand):
    def handle(self, *args, **options):
        generator = PairsGenerator()
        pairs = generator.generate_pairs()
        print(pairs[30][0])
        print(pairs[30][1])
        print(pairs[30][2])

        print("number", len(pairs))
