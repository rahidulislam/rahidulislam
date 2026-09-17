from datetime import date

from django.db import migrations


PROJECT = {
    'name': 'TheProperty',
    'short_desc': 'Role-aware Django marketplace for reviewed property listings in Bangladesh.',
    'description': 'A public architecture overview of a role-aware property marketplace.',
    'features': 'Django and PostgreSQL\nServer-side authorization\nProtected file delivery\nProduction-oriented operations',
    'problem': 'A property marketplace must balance public discovery with controlled publishing and private account data.',
    'contribution': 'I contributed the Django foundation, role-oriented workspaces, service boundaries, production configuration, and automated safeguards.',
    'technical_decisions': 'Public and private capabilities are separated through server-side authorization and explicit publishing controls. Internal moderation and commercial rules are omitted.',
    'outcome': 'The project demonstrates a production-oriented marketplace foundation without exposing private review processes or commercial logic.',
    'repository_url': 'https://github.com/rahidulislam/realestate_property',
    'is_published': True,
    'is_featured': False,
    'order': 4,
    'date': date(2026, 9, 3),
}


def add_project(apps, schema_editor):
    Category = apps.get_model('home', 'Category')
    Project = apps.get_model('home', 'Project')
    database = schema_editor.connection.alias
    if Project.objects.using(database).filter(name__iexact=PROJECT['name']).exists():
        return
    category, _ = Category.objects.using(database).get_or_create(name='Real estate marketplace')
    Project.objects.using(database).create(category=category, **PROJECT)


class Migration(migrations.Migration):
    dependencies = [('home', '0026_strengthen_project_contributions')]
    operations = [migrations.RunPython(add_project, migrations.RunPython.noop)]
