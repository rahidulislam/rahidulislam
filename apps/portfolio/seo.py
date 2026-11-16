from io import StringIO

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.xmlutils import SimplerXMLGenerator

from apps.articles.selectors import published_articles
from apps.profiles.presentation import profile_context
from apps.projects.selectors import published_projects
from core.seo import absolute_url


def sitemap_xml(request: HttpRequest) -> HttpResponse:
    # (path, last modified date or None)
    entries = [
        (reverse(name), None)
        for name in ("home:home", "home:projects", "home:articles", "home:experience")
    ]
    entries += [
        (reverse("home:case_study", args=[item.slug]), None)
        for item in published_projects().only("slug", "category")
    ]
    entries += [
        (reverse("home:article_detail", args=[item.slug]), item.published_at)
        for item in published_articles().only("slug", "published_at")
    ]
    entries += [
        (reverse("home:experience_detail", args=[item["slug"]]), None)
        for item in profile_context()["cv_profile"]["experience"]
    ]
    output = StringIO()
    xml = SimplerXMLGenerator(output, "utf-8")
    xml.startDocument()
    xml.startElement("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for path, modified in entries:
        xml.startElement("url", {})
        xml.startElement("loc", {})
        xml.characters(absolute_url(request, path))
        xml.endElement("loc")
        if modified:
            xml.startElement("lastmod", {})
            xml.characters(modified.isoformat())
            xml.endElement("lastmod")
        xml.endElement("url")
    xml.endElement("urlset")
    return HttpResponse(output.getvalue(), content_type="application/xml")


def robots_txt(request: HttpRequest) -> HttpResponse:
    sitemap = absolute_url(request, reverse("home:sitemap"))
    return HttpResponse(
        f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /dashboard/\nSitemap: {sitemap}\n",
        content_type="text/plain",
    )
