"""Count successful public documents once, including boosted HTMX navigation."""

import logging
from collections.abc import Callable

from django.db import DatabaseError
from django.http import HttpRequest, HttpResponse

from .services import record_navigation

logger = logging.getLogger(__name__)
BOT_MARKERS = (
    "bot",
    "spider",
    "crawler",
    "slurp",
    "headless",
    "facebookexternalhit",
    "preview",
)


class NavigationAnalyticsMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        match = request.resolver_match
        if (
            request.method != "GET"
            or response.status_code != 200
            or not response.get("Content-Type", "").startswith("text/html")
            or not match
            or match.namespace != "home"
            or len(request.path) > 500
            or request.user.is_authenticated
            or "preview" in request.GET
            or any(
                marker in request.META.get("HTTP_USER_AGENT", "").lower()
                for marker in BOT_MARKERS
            )
            or (
                request.headers.get("HX-Request") == "true"
                and request.headers.get("HX-Boosted") != "true"
                and request.headers.get("HX-History-Restore-Request") != "true"
            )
        ):
            return response
        try:
            record_navigation(request)
        except DatabaseError:
            # Do not log exception text: database errors can include event parameters.
            logger.warning("Analytics write failed; public response served.")
        return response
