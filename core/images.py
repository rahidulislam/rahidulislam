"""Intrinsic image sizes for width/height attributes, which prevent layout shift."""

import logging
from functools import lru_cache

from django.contrib.staticfiles import finders
from django.core.files.images import get_image_dimensions
from django.db.models.fields.files import ImageFieldFile

logger = logging.getLogger(__name__)
ImageSize = tuple[int, int]


def uploaded_image_size(image: ImageFieldFile | None) -> ImageSize | None:
    """Read only the header of an uploaded image; missing files yield None."""
    if not image:
        return None
    try:
        width, height = image.width, image.height
    except (OSError, ValueError):
        logger.warning("Image dimensions unavailable for %s", image.name)
        return None
    return (width, height) if width and height else None


@lru_cache(maxsize=128)
def static_image_size(path: str) -> ImageSize | None:
    """Return a static image's size, cached per process (files change on deploy)."""
    location = finders.find(path)
    if not location:
        return None
    width, height = get_image_dimensions(location)
    return (width, height) if width and height else None
