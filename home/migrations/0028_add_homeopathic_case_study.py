from datetime import date

from django.db import migrations


PROJECT = {
    'name': 'Homeopathic Management API',
    'short_desc': 'Role-aware Django API for appointments, clinical records, medicine stock, and billing.',
    'description': 'A public architecture overview of a role-aware clinic management API.',
    'features': 'Django REST Framework\nAuthenticated API access\nClinical and operational boundaries\nDocumented API contracts',
    'problem': 'A clinic platform coordinates scheduling, clinical records, inventory, and billing while protecting role and patient boundaries.',
    'contribution': 'I contributed authenticated APIs, permission boundaries, clinical workflow support, inventory integration, and billing foundations.',
    'technical_decisions': 'The public architecture uses documented APIs, server-side role enforcement, and validated state changes. Clinical rules and calculation logic are omitted.',
    'outcome': 'The project demonstrates an integrated clinic-management API while keeping medical, billing, and operational business rules private.',
    'repository_url': 'https://github.com/rahidulislam/homeopathic_ms',
    'is_published': True,
    'is_featured': False,
    'order': 5,
    'date': date(2025, 4, 30),
}


def add_project(apps, schema_editor):
    Category = apps.get_model('home', 'Category')
    Project = apps.get_model('home', 'Project')
    database = schema_editor.connection.alias
    if Project.objects.using(database).filter(name__iexact=PROJECT['name']).exists():
        return
    category, _ = Category.objects.using(database).get_or_create(name='Clinic management')
    Project.objects.using(database).create(category=category, **PROJECT)


class Migration(migrations.Migration):
    dependencies = [('home', '0027_add_theproperty_case_study')]
    operations = [migrations.RunPython(add_project, migrations.RunPython.noop)]
