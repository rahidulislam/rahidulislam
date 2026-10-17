from django.urls import path

from core.language import set_language

from .seo import robots_txt, sitemap_xml
from .views import HomeView

urlpatterns = [
    path("language/", set_language, name="set_language"),
    path("sitemap.xml", sitemap_xml, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    path("contact/", HomeView.as_view(), name="contact"),
    path("", HomeView.as_view(), name="home"),
]
