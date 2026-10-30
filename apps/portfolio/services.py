"""Domain content writes used by the owner dashboard."""

from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import transaction

from core.audit import record_change
from core.uploads import clean_failed_uploads

from .models import InformationCounter, Service, SiteBranding, Testimonial

Content = InformationCounter | Service | SiteBranding | Testimonial


def save_content(
    *, obj: Content, actor: AbstractBaseUser, changed_fields: list[str]
) -> Content:
    with clean_failed_uploads([obj]), transaction.atomic():
        adding = obj._state.adding
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
    if isinstance(obj, SiteBranding):
        raise ValidationError(
            "Site branding cannot be deleted. Clear uploaded images to restore defaults."
        )
    with transaction.atomic():
        record_change(
            actor=actor, obj=obj, action=DELETION, message="Deleted from dashboard"
        )
        obj.delete()
