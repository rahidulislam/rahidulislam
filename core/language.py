from collections.abc import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def language_context(request: HttpRequest) -> dict[str, str]:
    return {
        "portfolio_language": (
            "bn" if request.COOKIES.get("portfolio_language") == "bn" else "en"
        )
    }


@require_POST
def set_language(request: HttpRequest) -> HttpResponseRedirect:
    language = request.POST.get("language", "en")
    if language not in ("bn", "en"):
        language = "en"
    target = request.POST.get("next", "/")
    if not url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        target = "/"
    response = HttpResponseRedirect(target)
    response.set_cookie(
        "portfolio_language",
        language,
        max_age=31536000,
        samesite="Lax",
        secure=request.is_secure(),
    )
    return response


class LanguageVaryMiddleware:
    """Pages differ by the language cookie; tell caches not to mix them."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if response.get("Content-Type", "").startswith("text/html"):
            patch_vary_headers(response, ("Cookie",))
        return response
