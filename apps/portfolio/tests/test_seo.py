from datetime import date

from django.test import TestCase, override_settings

from apps.articles.models import Article


@override_settings(ALLOWED_HOSTS=["testserver", "www.example.com"])
class CanonicalUrlTests(TestCase):
    def test_configured_origin_wins_over_request_host(self):
        with override_settings(SITE_URL="https://example.com/"):
            page = self.client.get("/projects/", HTTP_HOST="www.example.com")
            sitemap = self.client.get("/sitemap.xml", HTTP_HOST="www.example.com")
            robots = self.client.get("/robots.txt", HTTP_HOST="www.example.com")
        self.assertContains(
            page, '<link rel="canonical" href="https://example.com/projects/">'
        )
        self.assertContains(page, 'content="https://example.com/static/img/og-')
        self.assertNotContains(page, "www.example.com")
        self.assertContains(sitemap, "<loc>https://example.com/projects/</loc>")
        self.assertNotContains(sitemap, "www.example.com")
        self.assertContains(robots, "Sitemap: https://example.com/sitemap.xml")

    def test_request_host_is_the_local_fallback(self):
        response = self.client.get("/projects/")
        self.assertContains(
            response, '<link rel="canonical" href="http://testserver/projects/">'
        )

    def test_contact_route_canonicalises_to_home(self):
        response = self.client.get("/contact/")
        self.assertContains(
            response, '<link rel="canonical" href="http://testserver/">'
        )
        self.assertContains(
            response, '<meta property="og:url" content="http://testserver/">'
        )

    def test_sitemap_reports_article_publication_date(self):
        Article.objects.create(
            slug="dated-article",
            title="Dated",
            summary="Summary",
            body="Body",
            topic="Topic",
            is_published=True,
            published_at=date(2026, 3, 4),
        )
        self.assertContains(
            self.client.get("/sitemap.xml"),
            "<loc>http://testserver/articles/dated-article/</loc>"
            "<lastmod>2026-03-04</lastmod>",
        )

    def test_pages_vary_on_the_language_cookie(self):
        self.assertIn("Cookie", self.client.get("/")["Vary"])
        self.assertNotIn("Vary", self.client.get("/robots.txt"))
