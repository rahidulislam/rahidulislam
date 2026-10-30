from django.http import HttpRequest

from .models import SiteBranding
from .selectors import site_branding_get


def site_branding(request: HttpRequest) -> dict[str, SiteBranding | None]:
    return {"site_branding": site_branding_get()}
