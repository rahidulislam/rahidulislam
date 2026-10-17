from django.urls import path

from .views import ExperienceDetailView, ExperienceListView

urlpatterns = [
    path("experience/", ExperienceListView.as_view(), name="experience"),
    path(
        "experience/<slug:slug>/",
        ExperienceDetailView.as_view(),
        name="experience_detail",
    ),
]
