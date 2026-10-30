from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.portfolio.models import SiteBranding, validate_brand_image_size
from apps.portfolio.services import delete_content


def image_upload(name="logo.png", size=(120, 40)):
    image = BytesIO()
    Image.new("RGB", size, "#176b64").save(image, "PNG")
    return SimpleUploadedFile(name, image.getvalue(), content_type="image/png")


class SiteBrandingTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_superuser(
            "brand-owner", "owner@example.test", "brand-test-password"
        )
        self.client.force_login(self.owner)
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.media = override_settings(MEDIA_ROOT=self.directory.name)
        self.media.enable()
        self.addCleanup(self.media.disable)

    def editor(self):
        return reverse("dashboard:add", args=["site-branding"])

    def test_defaults_are_readable_and_have_a_versioned_icon(self):
        response = self.client.get(reverse("home:articles"))
        self.assertContains(response, 'class="brand-word">rahidul.</span>', count=2)
        self.assertContains(response, "favicon.svg?v=20261030-navy-amber-logo")
        self.assertContains(response, "branding.css")

    def test_upload_updates_header_footer_and_both_site_icons_with_audit(self):
        response = self.client.post(
            self.editor(),
            {
                "brand_name": "Clear brand",
                "logo": image_upload(),
                "logo_dark": image_upload("dark.png"),
                "site_icon": image_upload("icon.png", (64, 64)),
            },
        )
        self.assertEqual(response.status_code, 302)
        branding = SiteBranding.objects.get()
        self.assertEqual(branding.pk, 1)
        self.assertTrue(branding.logo.storage.exists(branding.logo.name))
        public = self.client.get(reverse("home:articles"))
        self.assertContains(public, branding.logo.url, count=2)
        self.assertContains(public, branding.logo_dark.url, count=2)
        self.assertContains(public, branding.site_icon.url)
        self.assertContains(public, 'alt="Clear brand"')
        self.assertContains(
            self.client.get(reverse("dashboard:overview")), branding.site_icon.url
        )
        self.assertTrue(
            LogEntry.objects.filter(
                content_type__model="sitebranding", action_flag=ADDITION
            ).exists()
        )
        self.assertRedirects(self.client.get(self.editor()), response.url)

    def test_invalid_icon_or_file_retains_text_without_saving(self):
        for icon in [
            image_upload("rectangle.png"),
            image_upload("tiny.png", (16, 16)),
            SimpleUploadedFile(
                "unsafe.svg", b'<svg xmlns="http://www.w3.org/2000/svg"/>'
            ),
        ]:
            response = self.client.post(
                self.editor(), {"brand_name": "Keep my branding", "site_icon": icon}
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Keep my branding")
            self.assertFalse(SiteBranding.objects.exists())

    def test_clear_images_restores_text_and_default_icon(self):
        self.client.post(
            self.editor(),
            {
                "brand_name": "My brand",
                "logo": image_upload(),
                "site_icon": image_upload("icon.png", (64, 64)),
            },
        )
        response = self.client.post(
            reverse("dashboard:edit", args=["site-branding", 1]),
            {"brand_name": "Text brand", "logo-clear": "on", "site_icon-clear": "on"},
        )
        self.assertEqual(response.status_code, 302)
        branding = SiteBranding.objects.get()
        self.assertFalse(branding.logo)
        self.assertFalse(branding.site_icon)
        public = self.client.get(reverse("home:articles"))
        self.assertContains(public, "Text brand")
        self.assertContains(public, "favicon.svg?v=20261030-navy-amber-logo")

    def test_singleton_constraint_and_delete_protection(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            SiteBranding.objects.create(pk=2)
        branding = SiteBranding.objects.create()
        with self.assertRaises(ValidationError):
            delete_content(obj=branding, actor=self.owner)
        self.assertEqual(
            self.client.post(
                reverse("dashboard:delete", args=["site-branding", 1])
            ).status_code,
            404,
        )
        self.assertFalse(
            self.client.get(reverse("dashboard:list", args=["site-branding"])).context[
                "can_add"
            ]
        )

    def test_oversized_images_rejected(self):
        upload = image_upload()
        upload.size = 2 * 1024 * 1024 + 1
        with self.assertRaisesMessage(ValidationError, "2 MiB"):
            validate_brand_image_size(upload)

    def test_staff_cannot_edit_branding(self):
        user = get_user_model().objects.create_user("brand-staff", is_staff=True)
        self.client.force_login(user)
        self.assertEqual(
            self.client.post(self.editor(), {"brand_name": "Changed"}).status_code, 403
        )
        self.assertFalse(SiteBranding.objects.exists())
