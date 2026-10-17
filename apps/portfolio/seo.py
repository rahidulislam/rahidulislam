from io import StringIO

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.xmlutils import SimplerXMLGenerator

from apps.articles.selectors import published_articles
from apps.profiles.presentation import profile_context
from apps.projects.selectors import published_projects


def sitemap_xml(request: HttpRequest) -> HttpResponse:
    paths = [
        reverse("home:home"),
        reverse("home:projects"),
        reverse("home:articles"),
        reverse("home:experience"),
    ]
    paths += [
        reverse("home:case_study", args=[item.slug])
        for item in published_projects().only("slug", "category")
    ]
    paths += [
        reverse("home:article_detail", args=[item.slug])
        for item in published_articles().only("slug")
    ]
    paths += [
        reverse("home:experience_detail", args=[item["slug"]])
        for item in profile_context()["cv_profile"]["experience"]
    ]
    output = StringIO()
    xml = SimplerXMLGenerator(output, "utf-8")
    xml.startDocument()
    xml.startElement("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for path in paths:
        xml.startElement("url", {})
        xml.startElement("loc", {})
        xml.characters(request.build_absolute_uri(path))
        xml.endElement("loc")
        xml.endElement("url")
    xml.endElement("urlset")
    return HttpResponse(output.getvalue(), content_type="application/xml")


def robots_txt(request: HttpRequest) -> HttpResponse:
    sitemap = request.build_absolute_uri(reverse("home:sitemap"))
    return HttpResponse(
        f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {sitemap}\n",
        content_type="text/plain",
    )
