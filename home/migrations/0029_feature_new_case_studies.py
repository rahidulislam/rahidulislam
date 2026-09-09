from django.db import migrations


def feature_case_studies(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    Project.objects.using(schema_editor.connection.alias).filter(
        name__in=['TheProperty', 'Homeopathic Management API'],
    ).update(is_featured=True)


class Migration(migrations.Migration):
    dependencies = [('home', '0028_add_homeopathic_case_study')]
    operations = [migrations.RunPython(feature_case_studies, migrations.RunPython.noop)]
