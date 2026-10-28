"""Enquiry persistence and best-effort delivery, outside HTTP handlers."""

import logging
import smtplib
from dataclasses import dataclass
from functools import partial
from typing import Literal

from django.contrib.admin.models import ADDITION, CHANGE
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError
from django.db import transaction
from django.db.models import QuerySet

from core.audit import record_change
from core.uploads import clean_failed_uploads

from .integrations.email import send_enquiry_notification
from .models import Contact, PublicContact
from .selectors import failed_enquiries

logger = logging.getLogger(__name__)
DeliveryStatus = Literal["sent", "failed"]


@dataclass(frozen=True)
class EnquiryInput:
    name: str
    email: str
    subject: str
    message: str


def notify_contact(contact: Contact) -> DeliveryStatus:
    try:
        status: DeliveryStatus = (
            "sent" if send_enquiry_notification(contact) else "failed"
        )
    except (OSError, smtplib.SMTPException, BadHeaderError):
        logger.warning("Contact notification failed for enquiry %s", contact.pk)
        status = "failed"
    Contact.objects.filter(pk=contact.pk).update(notification_status=status)
    contact.notification_status = status
    return status


@transaction.atomic
def submit_enquiry(*, data: EnquiryInput) -> Contact:
    contact = Contact(
        name=data.name, email=data.email, subject=data.subject, message=data.message
    )
    contact.full_clean()
    contact.save()
    transaction.on_commit(partial(notify_contact, contact))
    return contact


def mark_enquiries(
    *, enquiries: QuerySet[Contact], status: Literal["read", "replied"]
) -> int:
    if status not in {"read", "replied"}:
        raise ValueError("Unsupported enquiry status")
    return enquiries.update(status=status)


def retry_notifications(*, enquiries: QuerySet[Contact]) -> int:
    return sum(
        notify_contact(item) == "sent"
        for item in failed_enquiries(enquiries=enquiries).iterator()
    )


@transaction.atomic
def update_enquiry_status(
    *, enquiry: Contact, status: Literal["read", "replied"], actor: AbstractBaseUser
) -> None:
    enquiry = Contact.objects.select_for_update().get(pk=enquiry.pk)
    mark_enquiries(enquiries=Contact.objects.filter(pk=enquiry.pk), status=status)
    record_change(
        actor=actor, obj=enquiry, action=CHANGE, message=f"Dashboard status: {status}"
    )


def retry_enquiry_notification(
    *, enquiry: Contact, actor: AbstractBaseUser
) -> DeliveryStatus:
    # Email is an external effect. Record the request atomically, then send after commit.
    with transaction.atomic():
        locked = Contact.objects.select_for_update().get(pk=enquiry.pk)
        if locked.notification_status != "failed":
            raise ValueError("Only failed notifications can be retried.")
        locked.notification_status = "pending"
        locked.save(update_fields=["notification_status"])
        record_change(
            actor=actor,
            obj=locked,
            action=CHANGE,
            message="Dashboard notification retry requested",
        )
    return notify_contact(locked)


def save_content(
    *, obj: PublicContact, actor: AbstractBaseUser, changed_fields: list[str]
) -> PublicContact:
    with clean_failed_uploads([obj]), transaction.atomic():
        if obj.pk is None and PublicContact.objects.exists():
            raise ValidationError(
                "Public contact details already exist. Edit the existing record."
            )
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


def delete_content(*, obj: PublicContact, actor: AbstractBaseUser) -> None:
    raise ValidationError(
        "Public contact details cannot be deleted. Clear optional fields instead."
    )
