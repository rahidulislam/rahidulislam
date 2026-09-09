from django.urls import path
from .views import HomeView, ProjectDetailView, CaseStudyView, download_cv
app_name = 'home'

urlpatterns = [
    path('cv/download/', download_cv, name='download_cv'),
    path('work/<slug:slug>/', CaseStudyView.as_view(), name='case_study'),
    path('', HomeView.as_view(), name='home'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
]
