from django.core.management.base import BaseCommand
from django.db import transaction
from home.models import Category, Project
from home.portfolio_content import fallback_projects


class Command(BaseCommand):
    help = 'Import the existing curated projects into admin without overwriting edits.'

    @transaction.atomic
    def handle(self, *args, **options):
        for index, item in enumerate(fallback_projects):
            if Project.objects.filter(name__iexact=item['name']).exists():
                continue
            category, _ = Category.objects.get_or_create(name=item['category'])
            Project.objects.create(
                name=item['name'], category=category, short_desc=item['short_desc'],
                description=item['description'], features='\n'.join(item['technical_notes']),
                is_featured=index < 3, order=index,
                **{key: item.get(key, "") for key in ("problem", "contribution", "technical_decisions", "outcome", "lessons")},
            )
            self.stdout.write(self.style.SUCCESS('Imported ' + item['name']))
