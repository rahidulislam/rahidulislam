from django.db import migrations


REPOSITORIES = {
    'TalentBridge': 'https://github.com/rahidulislam/talentbridge',
    'Smart Document Vault': 'https://github.com/rahidulislam/dms_saas',
    'HotelMotel': 'https://github.com/rahidulislam/hotelmotel_saas',
    'Portfolio Website': 'https://github.com/rahidulislam/rahidulislam',
}


def seed_repository_urls(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    for name, url in REPOSITORIES.items():
        Project.objects.using(schema_editor.connection.alias).filter(
            name__iexact=name,
            repository_url='',
        ).update(repository_url=url)


class Migration(migrations.Migration):
    dependencies = [('home', '0024_seed_case_studies')]
    operations = [migrations.RunPython(seed_repository_urls, migrations.RunPython.noop)]
