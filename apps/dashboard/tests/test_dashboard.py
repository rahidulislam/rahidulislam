from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.articles.models import Article
from apps.contacts.models import Contact, PublicContact
from apps.profiles.models import Skill
from apps.profiles.services import save_content
from apps.projects.models import Category, Project, ProjectImage

from ..forms import AnalyticsFilterForm
from ..resources import RESOURCES


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser(
            "owner", "owner@example.com", "strong-test-password"
        )
        cls.staff = get_user_model().objects.create_user(
            "editor", password="strong-test-password", is_staff=True
        )
        cls.skill = Skill.objects.create(
            name="Dashboard test skill", value=80, group="Core", order=0
        )
        cls.enquiry = Contact.objects.create(
            name="Visitor",
            email="visitor@example.com",
            subject="A conversation",
            message="Private message",
            notification_status="failed",
        )

    def setUp(self):
        self.client.force_login(self.owner)

    def url(self, name, **kwargs):
        return reverse("dashboard:" + name, kwargs=kwargs)

    def test_private_routes_require_owner_for_reads_and_writes(self):
        paths = [
            self.url("overview"),
            self.url("analytics"),
            self.url("inbox"),
            self.url("enquiry", pk=self.enquiry.pk),
            self.url("list", resource="skills"),
            self.url("add", resource="skills"),
            self.url("edit", resource="skills", pk=self.skill.pk),
            self.url("delete", resource="skills", pk=self.skill.pk),
            self.url("preview"),
            self.url("cv-preview"),
        ]
        self.client.logout()
        for path in paths:
            for method in [self.client.get, self.client.post]:
                with self.subTest(path=path, method=method.__name__):
                    self.assertEqual(method(path).status_code, 302)
        self.client.force_login(self.staff)
        for path in paths:
            for method in [self.client.get, self.client.post]:
                self.assertEqual(method(path).status_code, 403)

    def test_login_staff_rejected_owner_accepted_and_safe_next(self):
        self.client.logout()
        response = self.client.post(
            self.url("login"),
            {"username": "editor", "password": "strong-test-password"},
        )
        self.assertContains(response, "site owner only")
        response = self.client.post(
            self.url("login"),
            {
                "username": "owner",
                "password": "strong-test-password",
                "next": "https://evil.example/",
            },
        )
        self.assertRedirects(response, self.url("overview"))
        self.assertEqual(self.client.get(self.url("logout")).status_code, 405)
        self.assertRedirects(self.client.post(self.url("logout")), self.url("login"))
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        response = self.client.post(
            self.url("login"), {"username": "owner", "password": "strong-test-password"}
        )
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(response.status_code, 200)

    def test_csrf_required_for_writes_and_preview(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        for path in [
            self.url("add", resource="skills"),
            self.url("preview"),
            self.url("enquiry", pk=self.enquiry.pk),
            self.url("logout"),
        ]:
            self.assertEqual(client.post(path, {}).status_code, 403)

    def test_all_resource_lists_and_edit_forms_render(self):
        self.assertContains(self.client.get(self.url("overview")), "Published content")
        for resource in RESOURCES:
            with self.subTest(resource=resource.key):
                self.assertEqual(
                    self.client.get(
                        self.url("list", resource=resource.key)
                    ).status_code,
                    200,
                )
                response = self.client.get(
                    self.url("add", resource=resource.key), follow=True
                )
                self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url("list", resource="users"))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.url("analytics"))
        self.assertContains(response, "No data")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    def test_skill_validation_preserves_input_and_success_audits(self):
        url = self.url("add", resource="skills")
        response = self.client.post(
            url,
            {"name": "Keep this name", "value": "101", "group": "Core", "order": "0"},
        )
        self.assertContains(response, "Keep this name")
        self.assertFalse(Skill.objects.filter(name="Keep this name").exists())
        response = self.client.post(
            url, {"name": "New skill", "value": "95", "group": "Core", "order": "2"}
        )
        item = Skill.objects.get(name="New skill")
        self.assertRedirects(response, self.url("edit", resource="skills", pk=item.pk))
        self.assertTrue(
            LogEntry.objects.filter(
                object_id=str(item.pk), change_message__contains="Dashboard fields"
            ).exists()
        )
        self.assertEqual(
            self.client.post(
                self.url("edit", resource="skills", pk=item.pk),
                {"name": "Updated skill", "value": "90", "group": "Core", "order": "2"},
            ).status_code,
            302,
        )
        item.refresh_from_db()
        self.assertEqual(item.name, "Updated skill")

    def test_audit_failure_rolls_back_write(self):
        before = Skill.objects.count()
        with (
            patch(
                "apps.profiles.services.record_change",
                side_effect=DatabaseError("audit unavailable"),
            ),
            self.assertRaises(DatabaseError),
        ):
            save_content(
                obj=Skill(name="Not saved", value=70),
                actor=self.owner,
                changed_fields=["name"],
            )
        self.assertEqual(Skill.objects.count(), before)

    def test_delete_confirmation_and_audit_failure_rollback(self):
        from apps.profiles.services import delete_content

        url = self.url("delete", resource="skills", pk=self.skill.pk)
        self.assertContains(self.client.get(url), "Delete permanently")
        self.assertTrue(Skill.objects.filter(pk=self.skill.pk).exists())
        with (
            patch(
                "apps.profiles.services.record_change",
                side_effect=DatabaseError("audit unavailable"),
            ),
            self.assertRaises(DatabaseError),
        ):
            delete_content(obj=self.skill, actor=self.owner)
        self.assertTrue(Skill.objects.filter(pk=self.skill.pk).exists())
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertFalse(Skill.objects.filter(pk=self.skill.pk).exists())

    def test_search_pagination_and_related_filters(self):
        Skill.objects.bulk_create(
            [Skill(name=f"Findable {i}", value=50) for i in range(23)]
        )
        response = self.client.get(
            self.url("list", resource="skills"), {"q": "Findable", "page": "2"}
        )
        self.assertEqual(response.context["page"].paginator.count, 23)
        self.assertEqual(len(response.context["rows"]), 3)
        for value in ["invalid", "9" * 100]:
            response = self.client.get(
                self.url("list", resource="project-images"), {"project": value}
            )
            self.assertEqual(response.status_code, 200)

    def test_article_drafts_publication_and_safe_unsaved_preview(self):
        data = {
            "title": "Dashboard article",
            "slug": "dashboard-article",
            "topic": "Engineering",
            "summary": "A useful summary",
            "body": "## Safe preview\n<script>alert(1)</script>",
        }
        self.client.post(self.url("add", resource="articles"), data)
        item = Article.objects.get(slug="dashboard-article")
        anonymous = Client()
        self.assertEqual(
            anonymous.get(reverse("home:article_detail", args=[item.slug])).status_code,
            404,
        )
        data["is_published"] = "on"
        self.client.post(self.url("edit", resource="articles", pk=item.pk), data)
        self.assertEqual(
            anonymous.get(reverse("home:article_detail", args=[item.slug])).status_code,
            200,
        )
        response = self.client.post(
            self.url("preview"),
            {"body": "# Unsaved\n<script>alert(1)</script>\n[x](javascript:alert(1))"},
        )
        self.assertContains(response, "<h1>Unsaved</h1>")
        self.assertNotContains(response, "<script>")
        self.assertNotContains(response, 'href="javascript:')
        self.assertEqual(self.client.get(self.url("preview")).status_code, 405)
        item.refresh_from_db()
        self.assertEqual(item.body, data["body"])

    def test_upload_validation_and_rollback_cleanup(self):
        from apps.projects.services import save_content as save_project_content

        project = Project.objects.create(
            category=Category.objects.create(name="Dashboard"),
            name="Upload test",
            short_desc="Test",
        )
        data = {
            "project": project.pk,
            "kind": "screenshot",
            "order": "0",
            "image": SimpleUploadedFile(
                "invalid.png", b"not an image", content_type="image/png"
            ),
        }
        response = self.client.post(self.url("add", resource="project-images"), data)
        self.assertContains(response, "Upload a valid image")
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            image = BytesIO()
            Image.new("RGB", (2, 2), "white").save(image, "PNG")
            obj = ProjectImage(
                project=project,
                image=SimpleUploadedFile(
                    "valid.png", image.getvalue(), content_type="image/png"
                ),
            )
            with (
                patch(
                    "apps.projects.services.record_change",
                    side_effect=DatabaseError("audit unavailable"),
                ),
                self.assertRaises(DatabaseError),
            ):
                save_project_content(
                    obj=obj, actor=self.owner, changed_fields=["image"]
                )
            from pathlib import Path

            self.assertEqual(list(Path(directory).rglob("*.png")), [])
            self.assertFalse(ProjectImage.objects.filter(project=project).exists())

    def test_contact_singleton_and_delete_protection(self):
        from apps.contacts.services import delete_content, save_content

        existing = PublicContact.objects.first() or PublicContact.objects.create(
            email="owner@example.com"
        )
        response = self.client.get(self.url("add", resource="contact-details"))
        self.assertRedirects(
            response, self.url("edit", resource="contact-details", pk=existing.pk)
        )
        self.assertEqual(
            self.client.post(
                self.url("delete", resource="contact-details", pk=existing.pk)
            ).status_code,
            404,
        )
        with self.assertRaises(ValidationError):
            save_content(obj=PublicContact(), actor=self.owner, changed_fields=[])
        with self.assertRaises(ValidationError):
            delete_content(obj=existing, actor=self.owner)

    def test_enquiry_actions_retry_failure_and_search(self):
        url = self.url("enquiry", pk=self.enquiry.pk)
        self.client.post(url, {"action": "read"})
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, "read")
        self.client.post(url, {"action": "replied"})
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, "replied")
        with patch("apps.contacts.services.notify_contact", return_value="failed"):
            response = self.client.post(url, {"action": "retry"}, follow=True)
        self.assertContains(response, "delivery failed")
        response = self.client.post(url, {"action": "retry"})
        self.assertContains(response, "Only failed notifications")
        self.assertEqual(self.client.post(url, {"action": "unknown"}).status_code, 200)
        self.assertContains(
            self.client.get(
                self.url("inbox"), {"q": "Private message", "status": "replied"}
            ),
            "A conversation",
        )

    def test_cv_preview(self):
        with patch("apps.resumes.services.generate_cv", return_value=b"%PDF-test"):
            response = self.client.get(self.url("cv-preview"))
            self.assertEqual(response["Content-Type"], "application/pdf")
            self.assertNotIn("attachment", response.get("Content-Disposition", ""))
            self.assertEqual(b"".join(response.streaming_content), b"%PDF-test")

    def test_date_filters(self):
        for data in [
            {"period": "custom"},
            {"period": "custom", "start": "2026-10-10", "end": "2026-10-01"},
            {"period": "custom", "start": "2020-01-01", "end": "2026-01-01"},
            {"period": "oops"},
            {"period": "custom", "start": "nonsense", "end": "2026-01-01"},
        ]:
            self.assertFalse(AnalyticsFilterForm(data).is_valid())
        for period in ["7", "30", "90"]:
            form = AnalyticsFilterForm({"period": period})
            self.assertTrue(form.is_valid())
            self.assertEqual(
                (form.cleaned_data["end"] - form.cleaned_data["start"]).days,
                int(period) - 1,
            )

    def test_valid_image_upload_and_invalid_video_extension(self):
        project = Project.objects.create(
            category=Category.objects.create(name="Media test"),
            name="Media project",
            short_desc="Test",
        )
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            image = BytesIO()
            Image.new("RGB", (3, 3), "white").save(image, "PNG")
            response = self.client.post(
                self.url("add", resource="project-images"),
                {
                    "project": project.pk,
                    "kind": "screenshot",
                    "order": 0,
                    "caption": "Uploaded screenshot",
                    "alt_text": "Test image",
                    "image": SimpleUploadedFile(
                        "screen.png", image.getvalue(), content_type="image/png"
                    ),
                },
            )
            self.assertEqual(response.status_code, 302)
            item = ProjectImage.objects.get(project=project)
            self.assertTrue(item.image.storage.exists(item.image.name))
            self.assertTrue(
                LogEntry.objects.filter(
                    object_id=str(item.pk), content_type__model="projectimage"
                ).exists()
            )
        response = self.client.post(
            self.url("add", resource="project-videos"),
            {
                "project": project.pk,
                "order": 0,
                "file": SimpleUploadedFile(
                    "payload.exe", b"invalid", content_type="application/octet-stream"
                ),
            },
        )
        self.assertContains(response, "not allowed")

    def test_status_and_retry_requests_rollback_if_audit_fails(self):
        from apps.contacts.services import (
            retry_enquiry_notification,
            update_enquiry_status,
        )

        with (
            patch(
                "apps.contacts.services.record_change",
                side_effect=DatabaseError("audit unavailable"),
            ),
            self.assertRaises(DatabaseError),
        ):
            update_enquiry_status(enquiry=self.enquiry, status="read", actor=self.owner)
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, "unread")
        with (
            patch(
                "apps.contacts.services.record_change",
                side_effect=DatabaseError("audit unavailable"),
            ),
            patch("apps.contacts.services.notify_contact") as notify,
            self.assertRaises(DatabaseError),
        ):
            retry_enquiry_notification(enquiry=self.enquiry, actor=self.owner)
        notify.assert_not_called()
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.notification_status, "failed")

    def test_notification_retry_success_and_failure_are_persisted(self):
        from apps.contacts.services import retry_enquiry_notification

        with patch(
            "apps.contacts.services.send_enquiry_notification", return_value=False
        ):
            self.assertEqual(
                retry_enquiry_notification(enquiry=self.enquiry, actor=self.owner),
                "failed",
            )
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.notification_status, "failed")
        with patch(
            "apps.contacts.services.send_enquiry_notification", return_value=True
        ):
            self.assertEqual(
                retry_enquiry_notification(enquiry=self.enquiry, actor=self.owner),
                "sent",
            )
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.notification_status, "sent")
