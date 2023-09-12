# Generated by Django 4.2.5 on 2023-09-12 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_skill'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skill',
            name='value',
        ),
        migrations.AddField(
            model_name='skill',
            name='max_value',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='skill',
            name='min_value',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]