"""Portfolio facts verified against the Ilmora frontend source."""

MADRASHA_PROJECT = {'architecture_summary': 'A React Router SPA separates public pages from a shared management '
                         'shell. Typed domain services support session-scoped demo data and an API '
                         'adapter for future Django integration. Uploads persist in IndexedDB.',
 'category': 'Education management',
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
 'lessons': 'The next delivery phase is implementing and validating the Django API contract, '
            'server authentication, permissions and file handling before switching the frontend '
            'into API mode.',
 'name': 'Ilmora — Madrasha Management',
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
 'tags': ['React', 'TypeScript', 'Education', 'Bilingual UI'],
 'technical_decisions': 'Use a typed service boundary so the demo and future API integration share '
                        'frontend contracts.\n'
                        '\n'
                        'Keep academic-session data separate and store monetary values in integer '
                        'paisa.\n'
                        '\n'
                        'Provide separate public and workspace language/theme preferences, '
                        'responsive tables, CSV exports and printable reports.',
 'technical_notes': ['React 19, TypeScript, React Router 7 and Vite',
                     'TanStack Query and Zod with a typed service boundary',
                     'Academic-session records in browser storage; uploads in IndexedDB',
                     'Vitest and Playwright verification tooling'],
 'url': 'https://madrasha-backend.vercel.app/',
 'validation': 'Scope and architecture verified against the frontend README, route registry and '
               'project context. The live URL serves the Ilmora React SPA. The source includes '
               'Vitest domain tests and Playwright browser tests; these frontend suites were not '
               'rerun for this portfolio update.',
 'visual_label': 'Madrasha management frontend'}


MADRASHA_SCREENSHOTS = [
    {'image': 'img/projects/ilmora-landing.jpg', 'alt': 'Ilmora public landing page',
     'caption': 'Public website — Bengali landing page and demo entry.'},
    {'image': 'img/projects/ilmora-dashboard.jpg', 'alt': 'Ilmora administrator dashboard',
     'caption': 'Administrator demo dashboard — session statistics and institutional overview.'},
    {'image': 'img/projects/ilmora-students.jpg', 'alt': 'Ilmora student directory',
     'caption': 'Student directory — demo records, search and class filters.'},
]
MADRASHA_PROJECT['image'] = 'img/projects/ilmora-landing.jpg'
MADRASHA_PROJECT['image_alt'] = 'Ilmora bilingual madrasha management landing page'
