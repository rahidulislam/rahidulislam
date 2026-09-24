from django.urls import path
from .views import HomeView, LegacyProjectDetailView, CaseStudyView, download_cv, ProjectListView, health_check, sitemap_xml, robots_txt, ContactFormView, readiness
app_name = 'home'

urlpatterns = [
    path('sitemap.xml', sitemap_xml, name='sitemap'),
    path('robots.txt', robots_txt, name='robots'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('cv/download/', download_cv, name='download_cv'),
    path('work/<slug:slug>/', CaseStudyView.as_view(), name='case_study'),
    path('', HomeView.as_view(), name='home'),
    path('project/<int:pk>/', LegacyProjectDetailView.as_view(),
         name='project_detail'),
    path('health/', health_check, name='health_check'),
    path('readiness/', readiness, name='readiness'),
    path('contact/', ContactFormView.as_view(), name='contact'),
]
