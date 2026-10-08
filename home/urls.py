from django.urls import path
from .views import HomeView, LegacyProjectDetailView, CaseStudyView, download_cv, ProjectListView, ContactFormView, sitemap_xml, robots_txt
from .views import ArticleListView, ArticleDetailView, ExperienceListView, ExperienceDetailView
from .language import set_language
app_name = 'home'

urlpatterns = [
    path('language/', set_language, name='set_language'),
    path('articles/', ArticleListView.as_view(), name='articles'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('experience/', ExperienceListView.as_view(), name='experience'),
    path('experience/<slug:slug>/', ExperienceDetailView.as_view(), name='experience_detail'),
    path('sitemap.xml', sitemap_xml, name='sitemap'),
    path('robots.txt', robots_txt, name='robots'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('cv/download/', download_cv, name='download_cv'),
    path('work/<slug:slug>/', CaseStudyView.as_view(), name='case_study'),
    path('', HomeView.as_view(), name='home'),
    path('project/<int:pk>/', LegacyProjectDetailView.as_view(), name='project_detail'),
]
