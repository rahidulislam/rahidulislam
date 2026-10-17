from django.urls import path

from .views import CaseStudyView, LegacyProjectDetailView, ProjectListView

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="projects"),
    path("work/<slug:slug>/", CaseStudyView.as_view(), name="case_study"),
    path("project/<int:pk>/", LegacyProjectDetailView.as_view(), name="project_detail"),
]
