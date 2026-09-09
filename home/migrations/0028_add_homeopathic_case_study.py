from datetime import date

from django.db import migrations


PROJECT = {
    'name': 'Homeopathic Management API',
    'short_desc': 'Role-aware Django API for appointments, clinical records, medicine stock, and billing.',
    'description': 'A Django REST API that coordinates patients, doctors, receptionists, appointments, medical histories, prescriptions, medicine inventory, and appointment billing.',
    'features': 'Django REST Framework and JWT authentication\nDoctor availability and appointment status workflows\nSymptoms, family history, and prescription records\nMedicine suppliers, stock, discounts, and billing',
    'problem': 'A clinic needs to coordinate doctors, patients, receptionists, appointments, clinical records, medicine stock, and bills while keeping each action within the correct role boundary.',
    'contribution': 'I implemented role-based registration and permissions, doctor availability and appointment workflows, patient symptoms and family medical history, prescriptions and medicine inventory, and appointment billing with calculated bill items.',
    'technical_decisions': 'Django REST Framework and JWT authentication expose the clinic workflow through a documented API. Role-specific permission classes control doctor, patient, and receptionist actions.\n\nAppointment validation checks doctor availability and existing bookings, while explicit pending, confirmed, completed, and cancelled states represent the visit lifecycle.\n\nAppointment-linked medical history and prescriptions keep clinical context connected. Prescription duration determines medicine units, stock pricing supplies the current cost, and bill items are created together for the appointment.',
    'outcome': 'The repository exposes APIs for account registration, doctor availability, appointments, symptoms and family history, medical records, prescriptions, medicine categories and suppliers, stock pricing, and appointment billing.',
    'repository_url': 'https://github.com/rahidulislam/homeopathic_ms',
    'is_published': True,
    'is_featured': False,
    'order': 5,
    'date': date(2025, 4, 30),
}


def add_project(apps, schema_editor):
    Category = apps.get_model('home', 'Category')
    Project = apps.get_model('home', 'Project')
    database = schema_editor.connection.alias
    if Project.objects.using(database).filter(name__iexact=PROJECT['name']).exists():
        return
    category, _ = Category.objects.using(database).get_or_create(name='Clinic management')
    Project.objects.using(database).create(category=category, **PROJECT)


class Migration(migrations.Migration):
    dependencies = [('home', '0027_add_theproperty_case_study')]
    operations = [migrations.RunPython(add_project, migrations.RunPython.noop)]
