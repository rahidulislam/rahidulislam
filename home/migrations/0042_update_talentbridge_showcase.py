from django.db import migrations


def update_showcase(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    projects = Project.objects.using(schema_editor.connection.alias)
    projects.filter(name__iexact='TalentBridge').update(
        url='https://crm.tbcglobal.de/', image='',
    )


class Migration(migrations.Migration):
    dependencies = [('home', '0041_persist_experience_slugs')]
    operations = [migrations.RunPython(update_showcase, migrations.RunPython.noop)]
