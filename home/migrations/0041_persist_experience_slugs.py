from django.db import migrations, models
from django.utils.text import slugify


FALLBACK_SLUGS = {
    'talentbridge': 'talentbridge', 'wege': 'wege-llc',
    'meektec it': 'meektec-it', 'research rider': 'research-rider',
}


def populate_slugs(apps, schema_editor):
    Experience = apps.get_model('home', 'Experience')
    database = schema_editor.connection.alias
    used = set()
    for experience in Experience.objects.using(database).order_by('pk').iterator():
        identity = experience.company.casefold().strip()
        if identity in ('wege llc', 'wege general llc'):
            identity = 'wege'
        reserved = {slug for name, slug in FALLBACK_SLUGS.items() if name != identity}
        base = slugify(experience.company) or 'experience'
        candidate = base[:120]
        suffix = 2
        while candidate in used or candidate in reserved:
            suffix_text = f'-{suffix}'
            candidate = f'{base[:120 - len(suffix_text)]}{suffix_text}'
            suffix += 1
        Experience.objects.using(database).filter(pk=experience.pk).update(slug=candidate)
        used.add(candidate)


class Migration(migrations.Migration):
    dependencies = [('home', '0040_seed_engineering_articles')]
    operations = [
        migrations.AddField('experience', 'slug', models.SlugField(max_length=120, unique=True, null=True, blank=True)),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField('experience', 'slug', models.SlugField(max_length=120, unique=True, blank=True)),
    ]
