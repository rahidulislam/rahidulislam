"""Email transport; delivery policy belongs to the contact service."""

from django.conf import settings
from django.core.mail import EmailMessage

from ..models import Contact


def send_enquiry_notification(contact: Contact) -> bool:
    return (
        EmailMessage(
            subject=f"Portfolio enquiry: {contact.subject}",
            body=f"From: {contact.name} <{contact.email}>\n\n{contact.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_NOTIFICATION_EMAIL],
            reply_to=[contact.email],
        ).send(fail_silently=False)
        == 1
    )
