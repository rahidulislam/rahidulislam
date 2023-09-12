from django.urls import path
from .views import HomeView,ProjectDetailView
app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
]
