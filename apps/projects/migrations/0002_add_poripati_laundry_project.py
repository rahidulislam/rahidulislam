"""Publish the Poripati laundry case study; existing records are never overwritten."""

from django.db import migrations

# A frozen copy: later edits to apps/projects/laundry_content.py must not change
# what this historical migration inserts.
PROJECT = {
    "architecture_summary": "Django apps separate the catalogue, bag, orders, payments, "
    "dashboard and content. Pages are server-rendered and "
    "enhanced with HTMX for navigation, forms and live search, "
    "with full-page fallbacks. Celery workers handle email and "
    "payment verification; PostgreSQL and Redis back production.",
    "collaboration": "Independent product build",
    "constraints": "Business rules such as charges, cancellation cut-offs and refund "
    "policies are drafted for owner approval and are not invented by the "
    "software. Catalogue photographs are illustrative concept images.",
    "contribution": "Built the application end to end: the customer website, bag and "
    "checkout, order and payment workflows, the role-based staff "
    "workspace, the bilingual content editor and the deployment setup.",
    "contribution_areas": "Customer website, bag and checkout\n"
    "Order, payment and refund workflows\n"
    "Role-based staff workspace\n"
    "Bilingual content management\n"
    "Deployment and quality gates",
    "description": "A server-rendered Django and HTMX platform for a laundry and "
    "dry-cleaning business: customers browse priced garment services and "
    "order online in English or Bangla, while staff run orders, payments, "
    "refunds and website content from one workspace.",
    "development_status": "Live · bilingual web app",
    "features": "Django 5.2, HTMX 2 and Bootstrap 5.3\n"
    "Atomic checkout with price snapshots and audit events\n"
    "Celery workers for email and payment verification\n"
    "English and Bangla via Django gettext; WeasyPrint PDF invoices",
    "is_featured": False,
    "is_published": True,
    "lessons": "Separating delivery from payment and recording every change as an event "
    "made refunds and reporting far simpler than flag-based order states. "
    "Next: verify PostgreSQL row-lock behaviour under load in staging.",
    "name": "Poripati — Laundry Management",
    "order": 1,
    "outcome": "Customers can browse the catalogue, add garments and services to a bag, "
    "check out with cash on delivery or online payment, and download PDF "
    "invoices. Staff manage orders, customers, prices, refunds, business "
    "policies and site content through six permission-based roles.",
    "problem": "A laundry business needs customers to see clear prices and order without "
    "phone calls, and staff need one place to confirm, deliver and collect "
    "payment for orders, in both Bangla and English, on phones and desktops.",
    "project_role": "Full-stack Django Developer",
    "project_type": "Laundry ordering and operations platform",
    "short_desc": "Bilingual Django and HTMX app for laundry orders, payments and staff "
    "operations.",
    "slug": "poripati-laundry-management",
    "technical_decisions": "Save each order atomically and snapshot item prices, so later "
    "catalogue changes never alter past orders or revenue "
    "reports.\n"
    "\n"
    "Track confirmation, delivery and payment separately, and "
    "record events in an append-only audit history.\n"
    "\n"
    "Mark online payments as paid only after server-side gateway "
    "verification; refunds are recorded against confirmed receipts "
    "and can never exceed the paid balance.\n"
    "\n"
    "Use Django's translation framework for every interface string "
    "and keep business-authored content editable in both "
    "languages.",
    "technologies": "Python\nDjango\nHTMX\nPostgreSQL\nCelery\nBilingual UI",
    "url": "https://laundry-ms.rauhnova.com/",
    "validation": "Scope verified against the repository README, production-readiness "
    "notes and source. The repository's CI runs Ruff, Black, ESLint, Django "
    "system and migration checks, and roughly 270 automated tests covering "
    "checkout transactions, price snapshots, permissions, concurrency and "
    "PDF output; that suite was not rerun for this portfolio update. "
    "Screenshots were captured from the live public site.",
    "work_type": "fullstack",
}
CATEGORY = "Laundry operations"


def add_project(apps, schema_editor):
    database = schema_editor.connection.alias
    Category = apps.get_model("projects", "Category")
    Project = apps.get_model("projects", "Project")
    category, _ = Category.objects.using(database).get_or_create(name=CATEGORY)
    Project.objects.using(database).get_or_create(
        slug=PROJECT["slug"], defaults={**PROJECT, "category_id": category.pk}
    )


def remove_unedited_project(apps, schema_editor):
    """Undo only this migration's own insert; keep anything an editor changed."""
    database = schema_editor.connection.alias
    Category = apps.get_model("projects", "Category")
    Project = apps.get_model("projects", "Project")
    Project.objects.using(database).filter(category__name=CATEGORY, **PROJECT).delete()
    Category.objects.using(database).filter(
        name=CATEGORY, project_category__isnull=True
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("projects", "0001_initial")]
    operations = [migrations.RunPython(add_project, remove_unedited_project)]
