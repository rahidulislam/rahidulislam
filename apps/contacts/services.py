"""Enquiry persistence and best-effort delivery, outside HTTP handlers."""

import logging
import smtplib
from dataclasses import dataclass
from functools import partial
from typing import Literal

from django.core.mail import BadHeaderError
from django.db import transaction
from django.db.models import QuerySet

from .integrations.email import send_enquiry_notification
from .models import Contact
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
