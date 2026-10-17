from django.db.models import QuerySet

from .models import Contact, PublicContact


def public_contact_get() -> PublicContact | None:
    return PublicContact.objects.order_by("pk").first()


def failed_enquiries(*, enquiries: QuerySet[Contact]) -> QuerySet[Contact]:
    return enquiries.filter(notification_status="failed")
