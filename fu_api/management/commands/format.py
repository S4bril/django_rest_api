import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            subprocess.run(["isort", "."], check=True)
            subprocess.run(["black", "."], check=True)
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(e))
            return
