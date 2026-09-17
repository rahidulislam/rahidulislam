from django.db import migrations


CONTRIBUTIONS = {
    'TalentBridge': 'I contributed backend features, integration contracts, reliability improvements, and deployment support. Internal business rules are omitted.',
    'Smart Document Vault': 'I contributed tenant-aware access controls, secure processing, contract-aligned API behavior, and isolation-focused tests.',
    'HotelMotel': 'I contributed backend APIs, lifecycle handling, access controls, and automated tests across the hotel operations domain.',
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
