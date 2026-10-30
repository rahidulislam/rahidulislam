"""Shared audit boundary; callers include this write in their domain transaction."""

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


def record_change(
    *, actor: AbstractBaseUser, obj: Model, action: int, message: str
) -> None:
    LogEntry.objects.create(
        user_id=actor.pk,
        content_type=ContentType.objects.get_for_model(obj),
        object_id=str(obj.pk),
        object_repr=str(obj)[:200],
        action_flag=action,
        change_message=message,
    )
