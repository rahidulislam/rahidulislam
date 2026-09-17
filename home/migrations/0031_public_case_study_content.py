from django.db import migrations


PUBLIC_CONTENT = {
    'TalentBridge': {
        'problem': 'A recruitment platform must coordinate connected workflows while keeping organizational data appropriately separated and the API dependable as the product evolves.',
        'contribution': 'I contributed backend features, integration contracts, reliability improvements, and deployment support. Product-specific workflows and internal business rules are intentionally omitted.',
        'architecture_summary': 'A documented Django REST API separates request handling, background work, and persistent data. Authorization is enforced server-side at multiple boundaries. Detailed policies and domain relationships remain confidential.',
        'technical_decisions': 'The public architecture uses documented API contracts, server-side authorization, asynchronous processing, and environment-specific deployment configuration. Exact policies, workflow transitions, and operational rules are not disclosed.',
        'outcome': 'The work strengthened a documented recruitment API and its supporting reliability and deployment foundations. Internal workflows and business outcomes are not disclosed.',
        'challenges': [
            ('Protecting organizational boundaries', 'Prevent cross-context access in a connected recruitment domain.', 'Apply authorization and data scoping at server-controlled boundaries.', 'The access-control behavior is covered by focused automated tests.'),
            ('Keeping background work recoverable', 'Long-running work must not make API requests unreliable.', 'Separate background processing and make failure states explicit.', 'Worker and API responsibilities can be exercised independently.'),
        ],
    },
    'Smart Document Vault': {
        'problem': 'A multi-tenant document service must isolate customer data and treat uploaded files as untrusted until security checks complete.',
        'contribution': 'I contributed tenant-aware access controls, secure document processing, contract-aligned API behavior, and isolation-focused tests. Internal policy rules and storage topology are intentionally omitted.',
        'architecture_summary': 'A Django REST API enforces tenant and object boundaries before document operations reach private storage. Asynchronous security processing keeps unapproved files unavailable. Identifiers, policy rules, and storage topology remain confidential.',
        'technical_decisions': 'The design favors server-enforced isolation, fail-closed file availability, and retry-safe operations. Exact tenant resolution, policy evaluation, and processing rules are not published.',
        'outcome': 'The project demonstrates a security-first foundation for tenant-isolated document management, verified through automated access-control and API-contract tests.',
        'challenges': [
            ('Preserving tenant isolation', 'Every document operation must respect the active customer boundary.', 'Enforce isolation in backend data access and authorization layers.', 'Automated tests exercise allowed and denied access across tenant boundaries.'),
            ('Failing closed during file processing', 'Untrusted uploads must not become available when security infrastructure is delayed or unavailable.', 'Keep access dependent on an explicit approved processing state.', 'Failure-path tests confirm unavailable processing does not grant file access.'),
        ],
    },
}


SKILL_GROUPS = {
    'Python': 'Backend Engineering', 'Django': 'Backend Engineering',
    'Django REST Framework': 'Backend Engineering', 'REST APIs': 'Backend Engineering',
    'PostgreSQL': 'Database', 'MySQL': 'Database', 'SQLite': 'Database', 'Django ORM': 'Database',
    'JWT authentication': 'Authentication & Security', 'OAuth2': 'Authentication & Security',
    'Redis': 'Async & Caching', 'Celery': 'Async & Caching',
    'Docker': 'DevOps', 'Nginx': 'DevOps', 'GitHub Actions': 'DevOps', 'Git': 'DevOps', 'GitHub': 'DevOps',
    'Pytest': 'Testing & API Tools', 'OpenAPI': 'Testing & API Tools', 'Swagger': 'Testing & API Tools',
}


def seed_public_content(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    Challenge = apps.get_model('home', 'EngineeringChallenge')
    Skill = apps.get_model('home', 'Skill')
    database = schema_editor.connection.alias
    for name, content in PUBLIC_CONTENT.items():
        for project in Project.objects.using(database).filter(name__iexact=name):
            Project.objects.using(database).filter(pk=project.pk).update(**{
                key: value for key, value in content.items() if key != 'challenges'
            })
            if not Challenge.objects.using(database).filter(project_id=project.pk).exists():
                for order, (title, problem, approach, verification) in enumerate(content['challenges']):
                    Challenge.objects.using(database).create(
                        project_id=project.pk, title=title, problem=problem,
                        approach=approach, verification=verification, order=order,
                    )
    for order, skill in enumerate(Skill.objects.using(database).order_by('pk')):
        skill.group = SKILL_GROUPS.get(skill.name, 'Web & Tools')
        skill.order = order
        skill.save(update_fields=['group', 'order'])


class Migration(migrations.Migration):
    dependencies = [('home', '0030_alter_skill_options_project_api_docs_url_and_more')]
    operations = [migrations.RunPython(seed_public_content, migrations.RunPython.noop)]
