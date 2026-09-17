from django.db import migrations


PUBLIC_COPY = {
    'TalentBridge': (
        'Django REST backend for recruitment workflows.',
        'A public architecture overview of a Django REST recruitment platform. Domain rules, workflow transitions, data relationships, and organizational policies are intentionally omitted.',
        'Django REST Framework\nRelational persistence\nAsynchronous processing\nDocumented API contracts',
    ),
    'Smart Document Vault': (
        'Multi-tenant document-management API with secure isolation.',
        'A public architecture overview of a tenant-aware document service. Tenant resolution, policy logic, storage topology, and processing rules are intentionally omitted.',
        'Django REST Framework\nTenant-aware authorization\nAsynchronous security processing\nDocumented API contracts',
    ),
}


def tighten_copy(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    database = schema_editor.connection.alias
    for name, (short_desc, description, features) in PUBLIC_COPY.items():
        Project.objects.using(database).filter(name__iexact=name).update(
            short_desc=short_desc, description=description, features=features,
        )


class Migration(migrations.Migration):
    dependencies = [('home', '0031_public_case_study_content')]
    operations = [migrations.RunPython(tighten_copy, migrations.RunPython.noop)]
