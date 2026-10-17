from django.http import Http404
from django.views.generic import TemplateView

from .selectors import (
    article_by_slug,
    article_topics,
    published_articles,
    related_articles,
)


class ArticleListView(TemplateView):
    template_name = "home/articles.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()[:200]
        topic = self.request.GET.get("topic", "")
        data.update(
            topics=article_topics(),
            query=query,
            selected_topic=topic,
            articles=published_articles(query=query, topic=topic),
        )
        return data


class ArticleDetailView(TemplateView):
    template_name = "home/article_detail.html"

    def get_context_data(self, **kwargs):
        article = article_by_slug(slug=self.kwargs["slug"])
        if article is None:
            raise Http404("Article not found")
        return {
            **super().get_context_data(**kwargs),
            "article": article,
            "related_articles": related_articles(article=article),
        }
