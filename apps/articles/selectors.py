from django.db.models import Q, QuerySet

from .models import Article


def published_articles(*, query: str = "", topic: str = "") -> QuerySet[Article]:
    articles = Article.objects.filter(is_published=True)
    if query:
        articles = articles.filter(
            Q(title__icontains=query)
            | Q(title_bn__icontains=query)
            | Q(summary__icontains=query)
            | Q(summary_bn__icontains=query)
        )
    if topic:
        articles = articles.filter(topic=topic)
    return articles


def article_topics() -> QuerySet[str]:
    return (
        published_articles()
        .order_by("topic")
        .values_list("topic", flat=True)
        .distinct()
    )


def article_by_slug(*, slug: str) -> Article | None:
    return published_articles().filter(slug=slug).first()


def related_articles(*, article: Article) -> QuerySet[Article]:
    return published_articles(topic=article.topic).exclude(pk=article.pk)[:2]
