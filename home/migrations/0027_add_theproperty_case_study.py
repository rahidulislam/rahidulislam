from datetime import date

from django.db import migrations


PROJECT = {
    'name': 'TheProperty',
    'short_desc': 'Role-aware Django marketplace for reviewed property listings in Bangladesh.',
    'description': 'A server-rendered real-estate marketplace connecting buyers, sellers, agents, and staff through controlled listing, discovery, and inquiry workflows.',
    'features': 'Django 5.2 LTS and PostgreSQL\nBuyer, seller, agent, and staff workspaces\nModerated property publication lifecycle\nPrivate identity-document storage\nRedis rate limits and production operations',
    'problem': 'A property marketplace must let buyers discover relevant listings while giving sellers and agents controlled tools for publication and follow-up. Private identity documents and unpublished inventory must remain outside public access.',
    'contribution': 'I built the marketplace foundation and role-specific dashboards, completed the buyer journey, introduced buyer, seller, and agent application boundaries, and refactored business logic into selector and service layers. I also added production configuration, schema safeguards, tests, and operating documentation.',
    'technical_decisions': 'Email-based accounts use explicit buyer, seller, agent, and staff roles. Server-side checks protect each workspace rather than relying on hidden interface controls.\n\nProperties move through draft, review, published, rejected, sold, rented, and archived states. Atomic transition services and immutable status history make moderation decisions traceable.\n\nAgent identity files use private storage with permission-checked, audited downloads. PostgreSQL, Redis, S3-compatible storage, WhiteNoise, health checks, and structured logging form the production baseline.',
    'outcome': 'The first-release workflow supports reviewed sale and rent listings, property search, buyer favorites, questions and viewing requests, seller listing management, agent assignments, role dashboards, and staff moderation. Payment and commission workflows remain outside the current release scope.',
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
