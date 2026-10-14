from django import template
from django.utils.safestring import mark_safe
from home.article_content import render_article

register = template.Library()


@register.filter
def article_markdown(value):
    return mark_safe(render_article(value))
