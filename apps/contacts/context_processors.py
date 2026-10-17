from django.http import HttpRequest

from .models import PublicContact
from .selectors import public_contact_get


def public_contact(request: HttpRequest) -> dict[str, PublicContact | None]:
    return {"public_contact": public_contact_get()}
