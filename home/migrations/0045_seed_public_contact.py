from django.db import migrations


def seed_contact(apps, schema_editor):
    Contact = apps.get_model("home", "PublicContact")
    Person = apps.get_model("home", "PersonalInfo")
    Social = apps.get_model("home", "SocialMedia")
    alias = schema_editor.connection.alias
    person = Person.objects.using(alias).order_by("pk").first()
    links = {s.name.lower(): s.social_link for s in Social.objects.using(alias).all()}
    if not Contact.objects.using(alias).exists():
        Contact.objects.using(alias).create(
            email=person.email if person else "rahidulislam247@gmail.com",
            phone="+8801612061077",
            whatsapp="+8801612061077",
            location=person.address if person else "Bangladesh",
            linkedin=links.get(
                "linkedin", "https://www.linkedin.com/in/rahidulislam2023/"
            ),
            github=links.get("github", ""),
        )


class Migration(migrations.Migration):
    dependencies = [("home", "0044_publiccontact")]
    operations = [migrations.RunPython(seed_contact, migrations.RunPython.noop)]
