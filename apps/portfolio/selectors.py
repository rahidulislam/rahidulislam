from django.db.models import QuerySet

from .models import InformationCounter, Service, SiteBranding, Testimonial


def published_testimonials() -> QuerySet[Testimonial]:
    return Testimonial.objects.filter(consent_to_publish=True, is_published=True)


def information_counter_get() -> InformationCounter | None:
    return InformationCounter.objects.order_by("pk").first()


def service_list() -> QuerySet[Service]:
    return Service.objects.all()


def site_branding_get() -> SiteBranding | None:
    return SiteBranding.objects.filter(pk=1).first()
