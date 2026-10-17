from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.articles.models import Article
from apps.articles.rendering import render_article


class ArticleExperienceTests(TestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="Reliable APIs",
            title_bn="নির্ভরযোগ্য API",
            slug="reliable-apis",
            summary="Real engineering",
            body="## Decisions\n\n**Persist first**\n\n<script>alert(1)</script>",
            topic="Django",
            is_published=True,
        )
        Article.objects.create(
            title="Hidden draft",
            slug="hidden",
            summary="Draft",
            body="Draft",
            topic="Django",
        )

    def test_search_topic_and_draft_visibility(self):
        url = reverse("home:articles")
        self.assertContains(
            self.client.get(url, {"q": "Reliable", "topic": "Django"}), "Reliable APIs"
        )
        self.assertNotContains(self.client.get(url), "Hidden draft")
        self.assertContains(self.client.get(url, {"q": "unknown"}), "No articles found")
        self.assertEqual(
            self.client.get(
                reverse("home:article_detail", args=["hidden"])
            ).status_code,
            404,
        )

    def test_safe_markdown_and_cover_fallback(self):
        response = self.client.get(
            reverse("home:article_detail", args=[self.article.slug])
        )
        self.assertContains(response, "<h2>Decisions</h2>", html=True)
        self.assertContains(response, "<strong>Persist first</strong>")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "engineering-notes.svg")
        self.assertNotIn(
            'href="javascript:', render_article("[bad](javascript:alert(1))")
        )

    def test_admin_editor_preview_requires_authorization(self):
        url = reverse("admin:home_article_preview")
        self.assertEqual(self.client.post(url, {"body": "**hello**"}).status_code, 302)
        user = get_user_model().objects.create_superuser(
            "editor", "editor@example.com", "test-password"
        )
        self.client.force_login(user)
        response = self.client.post(url, {"body": "**hello** <script>bad</script>"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("<strong>hello</strong>", response.json()["html"])
        self.assertNotIn("<script>", response.json()["html"])
        self.assertContains(
            self.client.get(reverse("admin:home_article_add")),
            "article-markdown-editor",
        )

    def test_canonical_and_legacy_editor_preview_routes(self):
        user = get_user_model().objects.create_superuser(
            "route-editor", "editor@example.com", "test-password"
        )
        self.client.force_login(user)
        for name in ("admin:home_article_preview", "admin:articles_article_preview"):
            response = self.client.post(reverse(name), {"body": "**hello**"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()["html"].strip(), "<p><strong>hello</strong></p>"
            )
