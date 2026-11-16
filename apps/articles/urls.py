from django.urls import path

from .seo import LatestArticlesFeed
from .views import ArticleDetailView, ArticleListView

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/feed/", LatestArticlesFeed(), name="article_feed"),
    path("articles/<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
]
