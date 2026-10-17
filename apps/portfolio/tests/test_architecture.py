import ast
import json
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.profiles.models import PersonalInfo, SocialMedia


class DomainBoundaryTests(TestCase):
    def test_project_library_does_not_load_profile_history(self):
        with CaptureQueriesContext(connection) as queries:
            self.assertEqual(self.client.get("/projects/").status_code, 200)
        sql = " ".join(query["sql"].lower() for query in queries)
        for table in ("home_experience", "home_education", "home_skill"):
            self.assertNotIn(table, sql)

    def test_views_delegate_database_access(self):
        for path in (Path(settings.BASE_DIR) / "apps").glob("*/views.py"):
            tree = ast.parse(path.read_text())
            self.assertFalse(
                any(
                    isinstance(node, ast.Attribute) and node.attr == "objects"
                    for node in ast.walk(tree)
                ),
                path,
            )

    def test_domains_do_not_depend_on_legacy_home_modules(self):
        for path in (Path(settings.BASE_DIR) / "apps").rglob("*.py"):
            if "migrations" in path.parts or "tests" in path.parts:
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse((node.module or "").startswith("home."), path)

    def test_staff_permissions_work_with_new_and_legacy_admin_routes(self):
        user = get_user_model().objects.create_user(
            username="contact-reader", is_staff=True
        )
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="contacts", codename="view_contact"
            )
        )
        self.assertTrue(user.has_perm("home.view_contact"))
        self.assertTrue(user.has_perm("contacts.view_contact"))
        self.assertFalse(user.has_perm("home.change_article"))
        for backend in (
            "core.auth.LegacyPermissionBackend",
            "django.contrib.auth.backends.ModelBackend",
        ):
            self.client.force_login(user, backend=backend)
            for name in (
                "admin:contacts_contact_changelist",
                "admin:home_contact_changelist",
            ):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)
            self.assertEqual(
                self.client.get(
                    reverse("admin:articles_article_changelist")
                ).status_code,
                403,
            )

    def test_project_library_preserves_admin_identity_and_social_metadata(self):
        PersonalInfo.objects.create(
            name="Updated Owner",
            profession="Engineer",
            dob="1995-01-01",
            phone="+8801612061077",
            email="owner@example.com",
            age=31,
        )
        SocialMedia.objects.create(
            name="GitHub", social_link="https://github.com/updated-owner"
        )
        response = self.client.get("/projects/")
        self.assertContains(response, "Updated Owner")
        documents = [
            json.loads(body)
            for body in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                response.content.decode(),
            )
        ]
        person = next(item for item in documents if item["@type"] == "Person")
        self.assertIn("https://github.com/updated-owner", person["sameAs"])
