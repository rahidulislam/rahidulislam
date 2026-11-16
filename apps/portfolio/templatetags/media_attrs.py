from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def size_attrs(item) -> str:
    """Render width/height attributes from an object's get_image_size()."""
    size = item.get_image_size() if item else None
    if not size:
        return ""
    return format_html(' width="{}" height="{}"', size[0], size[1])
