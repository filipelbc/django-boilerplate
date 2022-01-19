from django.core.management.base import BaseCommand

from myapp.mock_data import create_mock_data


class Command(BaseCommand):
    help = 'Creates mock customers, devices, and readings'

    def handle(self, *args, **options):
        create_mock_data()
