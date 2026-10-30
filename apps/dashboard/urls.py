from django.urls import path

from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.index, name="overview"),
    path("login/", views.OwnerLoginView.as_view(), name="login"),
    path("logout/", views.OwnerLogoutView.as_view(), name="logout"),
    path("cv/preview/", views.cv_preview, name="cv-preview"),
    path("analytics/", views.analytics, name="analytics"),
    path("inbox/", views.inbox, name="inbox"),
    path("inbox/<int:pk>/", views.enquiry, name="enquiry"),
    path("articles/preview/", views.preview, name="preview"),
    path("content/<slug:resource>/", views.listing, name="list"),
    path("content/<slug:resource>/add/", views.editor, name="add"),
    path("content/<slug:resource>/<int:pk>/", views.editor, name="edit"),
    path("content/<slug:resource>/<int:pk>/delete/", views.delete, name="delete"),
]
