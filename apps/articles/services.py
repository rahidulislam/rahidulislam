"""Domain content writes used by the owner dashboard."""

from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction

from core.audit import record_change
from core.uploads import clean_failed_uploads

from .models import Article

Content = Article


def save_content(
    *, obj: Content, actor: AbstractBaseUser, changed_fields: list[str]
) -> Content:
    with clean_failed_uploads([obj]), transaction.atomic():
        adding = obj.pk is None
        obj.full_clean()
        obj.save()
        record_change(
            actor=actor,
            obj=obj,
            action=ADDITION if adding else CHANGE,
            message="Dashboard fields: " + ", ".join(changed_fields),
        )
    return obj


def delete_content(*, obj: Content, actor: AbstractBaseUser) -> None:
    with transaction.atomic():
        record_change(
            actor=actor, obj=obj, action=DELETION, message="Deleted from dashboard"
        )
        obj.delete()
