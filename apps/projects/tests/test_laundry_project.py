from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.projects.laundry_content import LAUNDRY_PROJECT, LAUNDRY_SCREENSHOTS
from apps.projects.models import Project

SLUG = LAUNDRY_PROJECT["slug"]


class LaundryProjectTests(TestCase):
    def test_migration_publishes_the_project(self):
        project = Project.objects.get(slug=SLUG)
        self.assertTrue(project.is_published)
        self.assertEqual(project.category.name, "Laundry operations")
        self.assertEqual(project.url, "https://laundry-ms.rauhnova.com/")
        self.assertEqual(project.work_type, "fullstack")
        self.assertIn("HTMX", project.technologies.splitlines())
        self.assertEqual(
            project.get_image_url(),
            "/static/img/projects/poripati/01-home-desktop-en.jpg",
        )

    def test_case_study_shows_live_link_and_screenshots(self):
        response = self.client.get(reverse("home:case_study", args=[SLUG]))
        self.assertContains(response, "<h1>Poripati — Laundry Management</h1>")
        self.assertContains(response, 'href="https://laundry-ms.rauhnova.com/"')
        for screenshot in LAUNDRY_SCREENSHOTS:
            self.assertContains(response, screenshot["image"])

    def test_library_filters_and_sitemap_include_the_project(self):
        projects = reverse("home:projects")
        for query in ({}, {"type": "fullstack"}, {"technology": "HTMX"}):
            with self.subTest(query=query):
                self.assertContains(
                    self.client.get(projects, query), "Poripati — Laundry Management"
                )
        self.assertNotContains(
            self.client.get(projects, {"type": "frontend"}), "Poripati"
        )
        self.assertContains(self.client.get("/sitemap.xml"), f"/work/{SLUG}/</loc>")

    def test_fallback_case_study_covers_fresh_installs(self):
        Project.objects.filter(slug=SLUG).delete()
        response = self.client.get(reverse("home:case_study", args=[SLUG]))
        self.assertContains(response, "Poripati — Laundry Management")
        self.assertContains(response, LAUNDRY_SCREENSHOTS[1]["image"])
        self.assertContains(self.client.get(reverse("home:projects")), "Poripati")

    def test_homepage_features_poripati_instead_of_the_portfolio(self):
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, f'href="/work/{SLUG}/"')
        self.assertContains(response, "poripati/01-home-desktop-en.jpg")
        self.assertNotContains(response, 'href="/work/portfolio-website/"')

    def test_screenshot_files_match_declared_sizes(self):
        static = Path(settings.BASE_DIR) / "static"
        for screenshot in LAUNDRY_SCREENSHOTS:
            with self.subTest(image=screenshot["image"]):
                with Image.open(static / screenshot["image"]) as image:
                    self.assertEqual(
                        image.size, (screenshot["width"], screenshot["height"])
                    )


class LaundryMigrationReverseTests(TestCase):
    def run_reverse(self):
        from importlib import import_module
        from types import SimpleNamespace

        from django.apps import apps
        from django.db import connection

        migration = import_module(
            "apps.projects.migrations.0002_add_poripati_laundry_project"
        )
        migration.remove_unedited_project(apps, SimpleNamespace(connection=connection))

    def test_reverse_removes_only_the_unedited_seed(self):
        self.run_reverse()
        self.assertFalse(Project.objects.filter(slug=SLUG).exists())

    def test_reverse_keeps_an_edited_project(self):
        Project.objects.filter(slug=SLUG).update(short_desc="Edited by the owner")
        self.run_reverse()
        self.assertTrue(Project.objects.filter(slug=SLUG).exists())
