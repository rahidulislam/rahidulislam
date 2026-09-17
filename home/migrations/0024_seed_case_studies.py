from django.db import migrations

CONTENT = {
    'TalentBridge': {
        'problem': 'A recruitment platform must coordinate connected workflows while keeping organizational data appropriately separated.',
        'contribution': 'I contributed backend features, integration contracts, reliability improvements, and deployment support. Internal business rules are omitted.',
        'technical_decisions': 'The public architecture uses documented API contracts, server-side authorization, asynchronous processing, and environment-specific configuration.',
        'outcome': 'The work strengthened the API and its reliability and deployment foundations without disclosing internal workflows.',
    },
    'Smart Document Vault': {
        'problem': 'A multi-tenant document service must isolate customer data and treat uploaded files as untrusted.',
        'technical_decisions': 'The public architecture favors server-enforced isolation, fail-closed file availability, and retry-safe operations.',
        'outcome': 'The project demonstrates a security-first document platform without publishing policy or processing rules.',
    },
    'HotelMotel': {
        'problem': 'Hotel operations require consistent records and careful authorization.',
        'technical_decisions': 'The public architecture separates major operational domains and uses explicit server-side permissions.',
        'outcome': 'The project demonstrates a tested hotel-operations API foundation without exposing workflow or pricing logic.',
    },
    'Portfolio Website': {
        'problem': 'Website and CV content must remain consistent as experience and work samples change.',
        'technical_decisions': 'Django admin manages published content and the website and generated PDF share one content provider.',
        'outcome': 'Visitors can browse projects and download a CV generated from current published content.',
    },
}


def seed(apps, schema_editor):
    Project = apps.get_model("home", "Project")
    for name, content in CONTENT.items():
        for project in Project.objects.using(schema_editor.connection.alias).filter(name__iexact=name):
            changed = []
            for field, value in content.items():
                if not getattr(project, field):
                    setattr(project, field, value)
                    changed.append(field)
            if changed:
                project.save(update_fields=changed)

class Migration(migrations.Migration):
    dependencies = [("home", "0023_project_contribution_project_lessons_project_outcome_and_more")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
