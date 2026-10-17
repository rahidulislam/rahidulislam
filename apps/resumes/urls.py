from django.urls import path

from .views import download_cv

urlpatterns = [
    path("cv/download/", download_cv, name="download_cv"),
]
