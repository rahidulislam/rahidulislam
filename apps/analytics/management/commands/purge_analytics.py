from django.core.management.base import BaseCommand

from apps.analytics.services import purge_details


class Command(BaseCommand):
    help = "Delete analytics event details and daily visitor hashes older than 90 days."

    def handle(self, *args, **options):
        events, visitors = purge_details()
        self.stdout.write(
            f"Deleted {events} events and {visitors} visitor hashes; aggregates retained."
        )
