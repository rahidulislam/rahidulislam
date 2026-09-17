from django.db import migrations


SUPERSEDED = {
    'TalentBridge': (
        'Protecting organizational boundaries',
        'Keeping background work recoverable',
    ),
    'Smart Document Vault': (
        'Preserving tenant isolation',
        'Failing closed during file processing',
    ),
}


def remove_superseded(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    Challenge = apps.get_model('home', 'EngineeringChallenge')
    database = schema_editor.connection.alias
    for project_name, titles in SUPERSEDED.items():
        project_ids = Project.objects.using(database).filter(
            name__iexact=project_name,
        ).values_list('pk', flat=True)
        Challenge.objects.using(database).filter(
            project_id__in=project_ids, title__in=titles,
        ).delete()


class Migration(migrations.Migration):
    dependencies = [('home', '0033_complete_safe_case_studies')]
    operations = [migrations.RunPython(remove_superseded, migrations.RunPython.noop)]
