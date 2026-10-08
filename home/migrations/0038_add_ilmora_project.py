from django.db import migrations


PROJECT = {'architecture_summary': 'A React Router SPA separates public pages from a shared management '
                         'shell. Typed domain services support session-scoped demo data and an API '
                         'adapter for future Django integration. Uploads persist in IndexedDB.',
 'collaboration': 'Frontend implementation project',
 'constraints': 'The deployed demo uses browser-local data and illustrative roles. Live Django '
                'APIs, payment gateways, SMS and biometric services are not connected; device '
                'synchronization is simulated.',
 'contribution': 'Completed the public website and management frontend, including responsive '
                 'screens, bilingual controls, validated forms and browser-persisted demo '
                 'workflows.',
 'contribution_areas': 'Responsive public website\n'
                       'Bangla and English interfaces\n'
                       'Admissions and student workflows\n'
                       'Attendance and finance screens\n'
                       'Typed service and API boundaries',
 'description': 'A completed React and TypeScript madrasha management frontend for administrators, '
                'teachers and accountants, with a responsive public website and interactive '
                'management workspace.',
 'development_status': 'Frontend complete · interactive demo',
 'features': 'React 19, TypeScript, React Router 7 and Vite\n'
             'TanStack Query and Zod with a typed service boundary\n'
             'Academic-session records in browser storage; uploads in IndexedDB\n'
             'Vitest and Playwright verification tooling',
 'is_featured': True,
 'is_published': True,
 'lessons': 'The next delivery phase is implementing and validating the Django API contract, '
            'server authentication, permissions and file handling before switching the frontend '
            'into API mode.',
 'name': 'Ilmora — Madrasha Management',
 'order': 1,
 'outcome': 'Delivered 58 management routes covering dashboard, admissions, students, attendance, '
            'fees, funds and administration, plus 12 public pages. The frontend supports '
            'multi-step admissions, student promotion, attendance marking, partial fee collection, '
            'receipts, donor records and audit filtering.',
 'problem': 'Madrasha staff need a connected interface for admissions, student records, attendance '
            'and finance, accessible in Bangla and English on desktop and mobile.',
 'project_role': 'Frontend Developer',
 'project_type': 'Madrasha management frontend',
 'repository_url': 'https://github.com/rahidulislam/madrasha_backend',
 'short_desc': 'Bilingual React frontend for admissions, attendance, fees and madrasha '
               'administration.',
 'slug': 'ilmora-madrasha-management',
 'technical_decisions': 'Use a typed service boundary so the demo and future API integration share '
                        'frontend contracts.\n'
                        '\n'
                        'Keep academic-session data separate and store monetary values in integer '
                        'paisa.\n'
                        '\n'
                        'Provide separate public and workspace language/theme preferences, '
                        'responsive tables, CSV exports and printable reports.',
 'url': 'https://madrasha-backend.vercel.app/',
 'validation': 'Scope and architecture verified against the frontend README, route registry and '
               'project context. The live URL serves the Ilmora React SPA. The source includes '
               'Vitest domain tests and Playwright browser tests; these frontend suites were not '
               'rerun for this portfolio update.'}


def add_project(apps, schema_editor):
    database = schema_editor.connection.alias
    Category = apps.get_model('home', 'Category')
    Project = apps.get_model('home', 'Project')
    category, _ = Category.objects.using(database).get_or_create(name='Education management')
    Project.objects.using(database).get_or_create(
        slug=PROJECT['slug'], defaults={**PROJECT, 'category_id': category.pk},
    )


class Migration(migrations.Migration):
    dependencies = [('home', '0037_add_live_project_urls')]
    operations = [migrations.RunPython(add_project, migrations.RunPython.noop)]
