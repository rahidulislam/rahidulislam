from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class PrivacyAndFontTests(TestCase):
    def test_privacy_page_is_public_linked_and_in_sitemap(self):
        response = self.client.get(reverse("home:privacy"))
        self.assertContains(response, "How this site handles your data.")
        self.assertContains(response, "deleted after 90 days")
        home = self.client.get(reverse("home:home"))
        # Linked from the footer and from the contact form note.
        self.assertContains(home, f'href="{reverse("home:privacy")}"', count=2)
        self.assertContains(self.client.get("/sitemap.xml"), "/privacy/</loc>")

    def test_privacy_page_is_translated(self):
        self.client.cookies["portfolio_language"] = "bn"
        self.assertContains(
            self.client.get(reverse("home:privacy")),
            "এই সাইট আপনার তথ্য কীভাবে ব্যবহার করে।",
        )

    def test_pages_load_no_third_party_fonts(self):
        response = self.client.get(reverse("home:home"))
        self.assertNotContains(response, "fonts.googleapis.com")
        self.assertNotContains(response, "fonts.gstatic.com")
        self.assertContains(response, "css/fonts.css")
        self.assertContains(response, "fonts/inter-latin-400-normal.woff2")

    def test_every_declared_font_file_exists(self):
        static = Path(settings.BASE_DIR) / "static"
        css = (static / "css/fonts.css").read_text()
        names = [part.split("')")[0] for part in css.split("url('../fonts/")[1:]]
        self.assertEqual(len(names), 16)
        for name in names:
            self.assertTrue((static / "fonts" / name).is_file(), name)
