"""Remove newly stored uploads if a database transaction rolls back."""

import logging
from collections.abc import Iterable, Iterator
from contextlib import contextmanager

from django.db.models import Model
from django.db.models.fields.files import FieldFile

logger = logging.getLogger(__name__)


@contextmanager
def clean_failed_uploads(objects: Iterable[Model]) -> Iterator[None]:
    uploads = [
        value
        for obj in objects
        for field in obj._meta.fields
        if isinstance(value := getattr(obj, field.name), FieldFile)
        and value.name
        and not value._committed
    ]
    try:
        yield
    except Exception:
        for upload in uploads:
            if upload._committed:
                try:
                    upload.storage.delete(upload.name)
                except OSError:
                    logger.warning(
                        "Upload cleanup failed after a rolled-back content write."
                    )
        raise
