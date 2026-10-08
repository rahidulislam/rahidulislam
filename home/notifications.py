"""Durable enquiry storage precedes best-effort email notification."""
import logging
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Contact

logger = logging.getLogger(__name__)


def notify_contact(contact):
    try:
        sent = EmailMessage(
            subject=f'Portfolio enquiry: {contact.subject}',
            body=f'From: {contact.name} <{contact.email}>\n\n{contact.message}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_NOTIFICATION_EMAIL],
            reply_to=[contact.email],
        ).send(fail_silently=False)
        status = 'sent' if sent == 1 else 'failed'
    except Exception:
        # Never log visitor content or credentials or lose an accepted enquiry.
        logger.warning('Contact notification failed for enquiry %s', contact.pk)
        status = 'failed'
    Contact.objects.filter(pk=contact.pk).update(notification_status=status)
    contact.notification_status = status
    return status
