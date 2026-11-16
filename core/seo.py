"""One public origin for canonical, social and sitemap URLs."""

from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse

# Routes that render another page's content and must not compete with it.
CANONICAL_ALIASES = {"home:contact": "home:home"}


def site_origin(request: HttpRequest) -> str:
    """Prefer the configured origin so www/apex/alias hosts share one URL."""
    configured = settings.SITE_URL.rstrip("/")
    return configured or f"{request.scheme}://{request.get_host()}"


def absolute_url(request: HttpRequest, path: str) -> str:
    return site_origin(request) + path


def canonical_path(request: HttpRequest) -> str:
    match = request.resolver_match
    alias = CANONICAL_ALIASES.get(match.view_name) if match else None
    return reverse(alias) if alias else request.path


def seo_context(request: HttpRequest) -> dict[str, str]:
    return {
        "site_origin": site_origin(request),
        "canonical_url": absolute_url(request, canonical_path(request)),
    }
