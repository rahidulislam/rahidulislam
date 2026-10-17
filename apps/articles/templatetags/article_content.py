from django import template
from django.utils.safestring import mark_safe

from apps.articles.rendering import render_article

register = template.Library()


@register.filter
def article_markdown(value):
    return mark_safe(render_article(value))
