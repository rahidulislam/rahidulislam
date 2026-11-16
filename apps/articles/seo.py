"""Machine-readable article metadata: schema.org JSON-LD and the RSS feed."""

import json
from datetime import datetime, time
from typing import Any

from django.contrib.syndication.views import Feed
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import SafeString, mark_safe

from core.seo import absolute_url

from .models import Article
from .selectors import published_articles

AUTHOR = "Md. Rahidul Islam"
FEED_SIZE = 20
# Characters that could close or confuse an HTML <script> block.
_SCRIPT_ESCAPES = {ord("<"): "\\u003c", ord(">"): "\\u003e", ord("&"): "\\u0026"}


def article_schema(*, article: Article, request: HttpRequest) -> SafeString:
    """Return schema.org Article JSON, escaped for inline use in a script tag."""
    url = absolute_url(request, reverse("home:article_detail", args=[article.slug]))
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.title,
        "description": article.summary,
        "url": url,
        "mainEntityOfPage": url,
        "image": absolute_url(request, article.cover_url),
        "author": {"@type": "Person", "name": AUTHOR},
        "inLanguage": ["en", "bn"] if article.title_bn else "en",
    }
    if article.published_at:
        data["datePublished"] = article.published_at.isoformat()
    payload = json.dumps(data, ensure_ascii=False).translate(_SCRIPT_ESCAPES)
    # Safe: JSON-encoded, with every HTML-significant character escaped above.
    return mark_safe(payload)


class LatestArticlesFeed(Feed):
    """RSS 2.0 feed of published articles with links on the canonical origin."""

    title = "Rahidul Islam — Engineering articles"
    description = "Notes on building reliable software with Python and Django."

    # Feed instances are shared between requests, so the request travels in obj.
    def get_object(self, request: HttpRequest) -> HttpRequest:
        return request

    def link(self, obj: HttpRequest) -> str:
        return absolute_url(obj, reverse("home:articles"))

    def feed_url(self, obj: HttpRequest) -> str:
        return absolute_url(obj, reverse("home:article_feed"))

    def items(self, obj: HttpRequest) -> list[tuple[Article, str]]:
        return [
            (
                article,
                absolute_url(obj, reverse("home:article_detail", args=[article.slug])),
            )
            for article in published_articles()[:FEED_SIZE]
        ]

    def item_title(self, item: tuple[Article, str]) -> str:
        return item[0].title

    def item_description(self, item: tuple[Article, str]) -> str:
        return item[0].summary

    def item_link(self, item: tuple[Article, str]) -> str:
        return item[1]

    def item_guid(self, item: tuple[Article, str]) -> str:
        return item[1]

    def item_author_name(self, item: tuple[Article, str]) -> str:
        return AUTHOR

    def item_pubdate(self, item: tuple[Article, str]) -> datetime | None:
        published = item[0].published_at
        if published is None:
            return None
        return timezone.make_aware(datetime.combine(published, time.min))
