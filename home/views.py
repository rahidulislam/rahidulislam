"""Legacy view imports. New routes belong in domain URL modules."""

from apps.articles.views import ArticleDetailView, ArticleListView
from apps.portfolio.seo import robots_txt, sitemap_xml
from apps.portfolio.views import HomeView
from apps.profiles.views import ExperienceDetailView, ExperienceListView
from apps.projects.views import CaseStudyView, LegacyProjectDetailView, ProjectListView
from apps.resumes.views import download_cv

ContactFormView = HomeView
__all__ = [
    "ArticleListView",
    "ArticleDetailView",
    "ExperienceListView",
    "ExperienceDetailView",
    "ProjectListView",
    "CaseStudyView",
    "LegacyProjectDetailView",
    "HomeView",
    "ContactFormView",
    "sitemap_xml",
    "robots_txt",
    "download_cv",
]
