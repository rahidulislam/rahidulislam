from django.core.management.base import BaseCommand
from django.db import transaction

from home.models import (
    Category, EngineeringChallenge, Project, ProjectImage, ProjectMetric,
)
from home.portfolio_content import fallback_projects


PROJECT_FIELDS = (
    'description', 'problem', 'contribution', 'architecture_summary',
    'technical_decisions', 'outcome', 'lessons', 'project_type',
    'project_role', 'collaboration', 'development_status',
    'contribution_areas', 'constraints', 'validation', 'url', 'api_docs_url',
)


class Command(BaseCommand):
    help = (
        'Import curated project case studies. Existing admin content is preserved '
        'unless --update-existing is supplied.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-existing', action='store_true',
            help='Update existing projects and matching child records from curated content.',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Report planned changes without writing to the database.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        update_existing = options['update_existing']
        dry_run = options['dry_run']
        counts = {'created': 0, 'updated': 0, 'skipped': 0}

        for index, item in enumerate(fallback_projects):
            project = (
                Project.objects.filter(slug=item['slug']).first()
                or Project.objects.filter(name__iexact=item['name']).first()
            )
            action = 'updated' if project else 'created'
            if project and not update_existing:
                counts['skipped'] += 1
                self.stdout.write(f"SKIP {item['slug']} (already exists)")
                continue
            if dry_run:
                counts[action] += 1
                verb = 'CREATE' if action == 'created' else 'UPDATE'
                self.stdout.write(f"WOULD {verb} {item['slug']}")
                continue

            category, _ = Category.objects.get_or_create(name=item['category'])
            values = {
                'name': item['name'], 'slug': item['slug'], 'category': category,
                'short_desc': item['short_desc'],
                'features': '\n'.join(item.get('technical_notes', [])),
                'is_featured': item.get('is_featured', index < 3),
                'is_published': item.get('is_published', True),
                'order': item.get('order', index),
            }
            values.update({field: item.get(field, '') for field in PROJECT_FIELDS})
            if project:
                for field, value in values.items():
                    setattr(project, field, value)
                project.save()
            else:
                project = Project.objects.create(**values)

            self._import_challenges(project, item.get('engineering_challenges', []))
            self._import_metrics(project, item.get('metrics', []))
            self._import_images(project, item.get('project_images', []))
            counts[action] += 1
            self.stdout.write(self.style.SUCCESS(f"{action.upper()} {item['slug']}"))

        if dry_run:
            transaction.set_rollback(True)
        self.stdout.write(
            f"Summary: {counts['created']} create, {counts['updated']} update, "
            f"{counts['skipped']} skip" + (' (dry run)' if dry_run else '')
        )

    @staticmethod
    def _import_challenges(project, challenges):
        for order, item in enumerate(challenges):
            EngineeringChallenge.objects.update_or_create(
                project=project, title=item['title'],
                defaults={
                    'problem': item.get('problem', ''),
                    'approach': item.get('approach', ''),
                    'solution': '',
                    'trade_offs': item.get('trade_offs', ''),
                    'verification': item.get('verification', ''),
                    'source_url': item.get('source_url', ''),
                    'is_published': item.get('is_published', True),
                    'order': item.get('order', order),
                },
            )

    @staticmethod
    def _import_metrics(project, metrics):
        for order, item in enumerate(metrics):
            ProjectMetric.objects.update_or_create(
                project=project, label=item['label'],
                defaults={
                    'value': item['value'],
                    'explanation': item.get('explanation', ''),
                    'source_url': item.get('source_url', ''),
                    'is_published': item.get('is_published', False),
                    'order': item.get('order', order),
                },
            )

    @staticmethod
    def _import_images(project, images):
        for order, item in enumerate(images):
            ProjectImage.objects.update_or_create(
                project=project, image=item['image'],
                defaults={
                    'caption': item.get('caption', ''),
                    'alt_text': item.get('alt_text', ''),
                    'kind': item.get('kind', ProjectImage.SCREENSHOT),
                    'order': item.get('order', order),
                },
            )
