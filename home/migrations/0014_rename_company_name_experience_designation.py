# Generated by Django 4.2.5 on 2023-09-12 06:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_alter_experience_end_year_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experience',
            old_name='company_name',
            new_name='designation',
        ),
    ]
