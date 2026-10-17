"""Stable public namespace; HTTP handlers live in their domain apps."""

from apps.articles.urls import urlpatterns as article_urls
from apps.portfolio.urls import urlpatterns as portfolio_urls
from apps.profiles.urls import urlpatterns as profile_urls
from apps.projects.urls import urlpatterns as project_urls
from apps.resumes.urls import urlpatterns as resume_urls

app_name = "home"
urlpatterns = article_urls + profile_urls + project_urls + resume_urls + portfolio_urls
