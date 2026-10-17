from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.contacts.models import PublicContact


class PublicContactTests(TestCase):
    def test_seeded_contact_is_visible_across_pages(self):
        for url in ("/", "/projects/", "/articles/"):
            response = self.client.get(url)
            self.assertContains(response, 'href="tel:+8801612061077"')
            self.assertContains(response, 'href="https://wa.me/8801612061077"')

    def test_database_updates_and_blank_fields(self):
        contact = PublicContact.objects.first()
        contact.phone = "+49123456789"
        contact.whatsapp = ""
        contact.telegram = "rahidul_test"
        contact.email = "hello@example.com"
        contact.save()
        response = self.client.get("/")
        self.assertContains(response, "tel:+49123456789")
        self.assertContains(response, "https://t.me/rahidul_test")
        self.assertContains(response, "mailto:hello@example.com")
        self.assertNotContains(response, "wa.me/")
        contact.telegram = ""
        contact.save()
        self.assertNotContains(self.client.get("/"), "https://t.me/")

    def test_contact_validation(self):
        contact = PublicContact(
            phone="javascript:alert(1)", telegram="https://t.me/test"
        )
        with self.assertRaises(ValidationError):
            contact.full_clean()
