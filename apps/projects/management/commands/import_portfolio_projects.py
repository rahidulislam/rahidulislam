from django.core.management.base import BaseCommand

from apps.projects.services import CatalogImporter


class Command(BaseCommand):
    help = "Import curated project case studies; existing admin content is preserved by default."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing curated records.",
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Report changes without writing."
        )

    def handle(self, *args, **options):
        CatalogImporter(self.stdout.write).run(
            update_existing=options["update_existing"], dry_run=options["dry_run"]
        )
