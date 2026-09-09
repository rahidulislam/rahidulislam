from django.db import migrations


def correct_wege_dates(apps, schema_editor):
    Experience = apps.get_model('home', 'Experience')
    for name in ('Wege', 'Wege LLC', 'Wege General LLC'):
        Experience.objects.filter(company__iexact=name).update(
            company='Wege LLC', start_year='Sep 2023', end_year='Jun 2024')


class Migration(migrations.Migration):
    dependencies = [('home', '0020_alter_education_end_year_alter_education_start_year')]
    operations = [migrations.RunPython(correct_wege_dates, migrations.RunPython.noop)]
