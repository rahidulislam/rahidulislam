"""Portfolio previews expose real captures and respect publication controls."""

from django.contrib.staticfiles import finders
from django.test import TestCase
from PIL import Image

from apps.projects.models import Category, Project


class PortfolioShowcaseTests(TestCase):
    def test_current_site_screenshots_are_available_in_case_study(self):
        response = self.client.get("/work/portfolio-website/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Captured from the current public portfolio")
        screenshots = response.context["static_screenshots"]
        self.assertEqual(len(screenshots), 2)
        for screenshot in screenshots:
            self.assertContains(response, screenshot["image"])
            self.assertContains(response, screenshot["alt"])
            with Image.open(finders.find(screenshot["image"])) as image:
                self.assertEqual(
                    image.size, (screenshot["width"], screenshot["height"])
                )

    def test_managed_portfolio_uses_capture_without_overriding_uploaded_image(self):
        project = Project.objects.create(
            name="Portfolio Website",
            category=Category.objects.create(name="Personal site"),
            slug="portfolio-website",
        )
        self.assertIn("portfolio-website/01-home-desktop.png", project.get_image_url())
        response = self.client.get("/work/portfolio-website/")
        self.assertEqual(len(response.context["static_screenshots"]), 2)
        project.image = "images/custom-portfolio.png"
        self.assertEqual(project.get_image_url(), "/media/images/custom-portfolio.png")
        project.is_published = False
        project.save()
        self.assertEqual(self.client.get("/work/portfolio-website/").status_code, 404)
        home = self.client.get("/")
        self.assertNotContains(home, "View Portfolio Website case study")
