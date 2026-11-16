import json
import re
from datetime import date

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.articles.models import Article


@override_settings(SITE_URL="https://example.com")
class ArticleFeedAndSchemaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = Article.objects.create(
            slug="schema-article",
            title="Schema </script><b>title</b>",
            summary="Summary & details",
            body="Body",
            topic="Topic",
            is_published=True,
            published_at=date(2026, 5, 6),
        )
        Article.objects.create(
            slug="draft-feed-article",
            title="Draft",
            summary="Hidden",
            body="Draft",
            topic="Private",
        )

    def test_article_page_has_safe_article_json_ld(self):
        response = self.client.get(
            reverse("home:article_detail", args=[self.article.slug])
        )
        html = response.content.decode()
        self.assertNotIn("</script><b>", html)
        blocks = re.findall(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
        )
        article = next(
            data for data in map(json.loads, blocks) if data["@type"] == "Article"
        )
        self.assertEqual(article["headline"], self.article.title)
        self.assertEqual(article["datePublished"], "2026-05-06")
        self.assertEqual(article["url"], "https://example.com/articles/schema-article/")
        self.assertEqual(article["author"]["name"], "Md. Rahidul Islam")

    def test_feed_lists_published_articles_on_the_canonical_origin(self):
        response = self.client.get(reverse("home:article_feed"))
        self.assertEqual(response["Content-Type"], "application/rss+xml; charset=utf-8")
        body = response.content.decode()
        self.assertIn("<link>https://example.com/articles/schema-article/</link>", body)
        self.assertIn("Summary &amp; details", body)
        self.assertNotIn("draft-feed-article", body)
        self.assertIn("Wed, 06 May 2026", body)

    def test_pages_advertise_the_feed(self):
        self.assertContains(
            self.client.get(reverse("home:home")),
            'type="application/rss+xml" title="Rahidul Islam — Engineering articles" '
            'href="/articles/feed/"',
        )
