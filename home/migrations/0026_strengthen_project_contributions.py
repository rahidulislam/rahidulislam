from django.db import migrations


CONTRIBUTIONS = {
    'TalentBridge': 'As a Mid Level Python Developer, I implemented and hardened employer onboarding, partner company updates, self-service profiles, password changes, and invitation recovery flows. I also contributed deployment, CI, demo-data, and API documentation improvements.',
    'Smart Document Vault': 'I implemented tenant-scoped data access and object authorization across document and folder operations, added role and tenant test matrices, and aligned API response and error contracts with the published OpenAPI schema.',
    'HotelMotel': 'I implemented hotel and room endpoints, booking creation, listing and detail APIs, and later expanded the booking lifecycle with confirmation, cancellation, check-in, checkout, no-show flows, hotel-context permissions, and automated tests.',
}


def strengthen_contributions(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    database = schema_editor.connection.alias
    generic_talentbridge = 'Mid Level Python Developer at TalentBridge, working remotely with the Germany-based team since June 2026.'
    for name, contribution in CONTRIBUTIONS.items():
        projects = Project.objects.using(database).filter(name__iexact=name)
        if name == 'TalentBridge':
            projects = projects.filter(contribution__in=['', generic_talentbridge])
        else:
            projects = projects.filter(contribution='')
        projects.update(contribution=contribution)


class Migration(migrations.Migration):
    dependencies = [('home', '0025_seed_project_repository_urls')]
    operations = [migrations.RunPython(strengthen_contributions, migrations.RunPython.noop)]
