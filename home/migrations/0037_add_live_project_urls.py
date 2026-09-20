from django.db import migrations


LIVE_URLS = {
    'Smart Document Vault': 'https://dms-frontend-six-sandy.vercel.app/',
    'Homeopathic Management API': 'https://homeopathicfrontend.vercel.app/',
    'HotelMotel': 'https://hotelmotelfrontend.vercel.app/',
    'TheProperty': 'https://7of6r13knd.execute-api.ap-south-1.amazonaws.com/dev/',
}


def add_live_urls(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    database = schema_editor.connection.alias
    for name, url in LIVE_URLS.items():
        Project.objects.using(database).filter(name__iexact=name).update(url=url)


def remove_live_urls(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    database = schema_editor.connection.alias
    for name, url in LIVE_URLS.items():
        Project.objects.using(database).filter(name__iexact=name, url=url).update(url='')


class Migration(migrations.Migration):
    dependencies = [('home', '0036_seed_recruiter_case_study_facts')]
    operations = [migrations.RunPython(add_live_urls, remove_live_urls)]
