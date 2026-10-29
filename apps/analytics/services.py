"""Persist privacy-limited events and increment aggregates atomically."""

from datetime import timedelta
from ipaddress import ip_address
from urllib.parse import urlsplit

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import DailyPage, DailyReferrer, DailyTraffic, DailyVisitor, PageView


def visitor_key(request: HttpRequest, day: str) -> str:
    address = request.META.get("REMOTE_ADDR", "")
    trusted = settings.ANALYTICS_TRUSTED_PROXIES
    if address in trusted:
        chain = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")
        for candidate in reversed(chain):
            candidate = candidate.strip()
            try:
                ip_address(candidate)
            except ValueError:
                break
            address = candidate
            if address not in trusted:
                break
    return salted_hmac(
        f"portfolio.analytics.{day}",
        address + "\n" + request.META.get("HTTP_USER_AGENT", "")[:512],
        algorithm="sha256",
    ).hexdigest()


def referrer_domain(request: HttpRequest) -> str:
    try:
        parsed = urlsplit(request.META.get("HTTP_REFERER", "")[:2048])
        if parsed.scheme not in {"http", "https"}:
            return ""
        domain = (parsed.hostname or "").encode("idna").decode("ascii").lower()
        if domain == request.get_host().split(":")[0].lower() or len(domain) > 253:
            return ""
        return domain
    except (ValueError, UnicodeError):
        return ""


@transaction.atomic
def record_navigation(request: HttpRequest) -> None:
    day = timezone.localdate()
    traffic, _ = DailyTraffic.objects.get_or_create(date=day)
    # Acquire the day's write lock before checking visitor uniqueness.
    DailyTraffic.objects.filter(pk=traffic.pk).update(views=F("views") + 1)
    _, created = DailyVisitor.objects.get_or_create(
        date=day, key=visitor_key(request, day.isoformat())
    )
    if created:
        DailyTraffic.objects.filter(pk=traffic.pk).update(visitors=F("visitors") + 1)
    domain = referrer_domain(request)
    page, _ = DailyPage.objects.get_or_create(date=day, path=request.path)
    DailyPage.objects.filter(pk=page.pk).update(views=F("views") + 1)
    referral, _ = DailyReferrer.objects.get_or_create(date=day, domain=domain)
    DailyReferrer.objects.filter(pk=referral.pk).update(views=F("views") + 1)
    PageView.objects.create(path=request.path, referrer=domain)


@transaction.atomic
def purge_details() -> tuple[int, int]:
    cutoff = timezone.localdate() - timedelta(days=90)
    events, _ = PageView.objects.filter(created_at__date__lt=cutoff).delete()
    visitors, _ = DailyVisitor.objects.filter(date__lt=cutoff).delete()
    return events, visitors
