"""Bounded aggregate queries for the private dashboard."""

from datetime import date, timedelta

from django.db.models import Sum

from .models import DailyPage, DailyReferrer, DailyTraffic


def traffic_report(*, start: date, end: date) -> dict:
    rows = list(DailyTraffic.objects.filter(date__range=(start, end)))
    tracking_since = (
        DailyTraffic.objects.order_by("date").values_list("date", flat=True).first()
    )
    first_day = max(start, tracking_since) if tracking_since else start
    by_date = {row.date: row for row in rows}
    maximum = max((row.views for row in rows), default=1) or 1
    days = []
    if tracking_since:
        for offset in range((end - first_day).days + 1):
            day = first_day + timedelta(days=offset)
            row = by_date.get(day)
            views, visitors = (row.views, row.visitors) if row else (0, 0)
            days.append(
                {
                    "date": day,
                    "views": views,
                    "visitors": visitors,
                    "percent": round(views * 100 / maximum, 2),
                }
            )
    return {
        "days": days,
        "total_views": sum(row.views for row in rows),
        "visitor_days": sum(row.visitors for row in rows),
        "has_data": bool(tracking_since and end >= tracking_since),
        "tracking_since": tracking_since,
        "pages": list(
            DailyPage.objects.filter(date__range=(start, end))
            .values("path")
            .annotate(views=Sum("views"))
            .order_by("-views", "path")[:20]
        ),
        "referrers": list(
            DailyReferrer.objects.filter(date__range=(start, end))
            .values("domain")
            .annotate(views=Sum("views"))
            .order_by("-views", "domain")[:20]
        ),
    }
