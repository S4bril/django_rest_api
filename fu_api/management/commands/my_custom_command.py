from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'My custom command description'

    def handle(self, *args, **options):
        self.stdout.write("Running custom command!")
        # Add your custom logic here