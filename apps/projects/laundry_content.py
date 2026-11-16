"""Portfolio facts verified against the Poripati laundry_ms source and live site."""

LAUNDRY_PROJECT = {
    "slug": "poripati-laundry-management",
    "name": "Poripati — Laundry Management",
    "category": "Laundry operations",
    "work_type": "fullstack",
    "project_role": "Full-stack Django Developer",
    "project_type": "Laundry ordering and operations platform",
    "collaboration": "Independent product build",
    "development_status": "Live · bilingual web app",
    "url": "https://laundry-ms.rauhnova.com/",
    "short_desc": "Bilingual Django and HTMX app for laundry orders, payments and "
    "staff operations.",
    "description": "A server-rendered Django and HTMX platform for a laundry and "
    "dry-cleaning business: customers browse priced garment services and order "
    "online in English or Bangla, while staff run orders, payments, refunds and "
    "website content from one workspace.",
    "problem": "A laundry business needs customers to see clear prices and order "
    "without phone calls, and staff need one place to confirm, deliver and collect "
    "payment for orders, in both Bangla and English, on phones and desktops.",
    "contribution": "Built the application end to end: the customer website, bag "
    "and checkout, order and payment workflows, the role-based staff workspace, "
    "the bilingual content editor and the deployment setup.",
    "contribution_areas": "Customer website, bag and checkout\n"
    "Order, payment and refund workflows\n"
    "Role-based staff workspace\n"
    "Bilingual content management\n"
    "Deployment and quality gates",
    "architecture_summary": "Django apps separate the catalogue, bag, orders, "
    "payments, dashboard and content. Pages are server-rendered and enhanced with "
    "HTMX for navigation, forms and live search, with full-page fallbacks. Celery "
    "workers handle email and payment verification; PostgreSQL and Redis back "
    "production.",
    "technical_decisions": "Save each order atomically and snapshot item prices, so "
    "later catalogue changes never alter past orders or revenue reports.\n"
    "\n"
    "Track confirmation, delivery and payment separately, and record events in an "
    "append-only audit history.\n"
    "\n"
    "Mark online payments as paid only after server-side gateway verification; "
    "refunds are recorded against confirmed receipts and can never exceed the paid "
    "balance.\n"
    "\n"
    "Use Django's translation framework for every interface string and keep "
    "business-authored content editable in both languages.",
    "outcome": "Customers can browse the catalogue, add garments and services to a "
    "bag, check out with cash on delivery or online payment, and download PDF "
    "invoices. Staff manage orders, customers, prices, refunds, business policies "
    "and site content through six permission-based roles.",
    "constraints": "Business rules such as charges, cancellation cut-offs and refund "
    "policies are drafted for owner approval and are not invented by the software. "
    "Catalogue photographs are illustrative concept images.",
    "validation": "Scope verified against the repository README, production-"
    "readiness notes and source. The repository's CI runs Ruff, Black, ESLint, "
    "Django system and migration checks, and roughly 270 automated tests covering "
    "checkout transactions, price snapshots, permissions, concurrency and PDF "
    "output; that suite was not rerun for this portfolio update. Screenshots were "
    "captured from the live public site.",
    "lessons": "Separating delivery from payment and recording every change as an "
    "event made refunds and reporting far simpler than flag-based order states. "
    "Next: verify PostgreSQL row-lock behaviour under load in staging.",
    "technical_notes": [
        "Django 5.2, HTMX 2 and Bootstrap 5.3",
        "Atomic checkout with price snapshots and audit events",
        "Celery workers for email and payment verification",
        "English and Bangla via Django gettext; WeasyPrint PDF invoices",
    ],
    "tags": ["Python", "Django", "HTMX", "PostgreSQL", "Celery", "Bilingual UI"],
    "visual_label": "Laundry ordering and operations",
    "image": "img/projects/poripati/01-home-desktop-en.jpg",
    "image_alt": "Poripati laundry website homepage",
}

LAUNDRY_SCREENSHOTS = [
    {
        "image": "img/projects/poripati/01-home-desktop-en.jpg",
        "alt": "Poripati homepage in English",
        "caption": "Customer website — English homepage.",
        "width": 1440,
        "height": 1000,
    },
    {
        "image": "img/projects/poripati/02-price-list-en.jpg",
        "alt": "Poripati services and prices catalogue",
        "caption": "Services & prices — searchable garment catalogue.",
        "width": 1440,
        "height": 1000,
    },
    {
        "image": "img/projects/poripati/03-garment-detail-en.jpg",
        "alt": "Poripati garment detail with service and quantity selection",
        "caption": "Garment detail — choose a service and add it to the bag.",
        "width": 1440,
        "height": 1000,
    },
    {
        "image": "img/projects/poripati/04-home-mobile-bn.jpg",
        "alt": "Poripati Bangla homepage on mobile",
        "caption": "Mobile — Bangla interface at 390px width.",
        "width": 390,
        "height": 844,
    },
    {
        "image": "img/projects/poripati/05-home-desktop-dark-en.jpg",
        "alt": "Poripati homepage in dark mode",
        "caption": "Dark theme — the same pages in a dark palette.",
        "width": 1440,
        "height": 1000,
    },
    {
        "image": "img/projects/poripati/06-staff-dashboard-dark-en.jpg",
        "alt": "Poripati staff workspace overview",
        "caption": "Staff workspace — overview on an empty demo database.",
        "width": 1440,
        "height": 1000,
    },
]
