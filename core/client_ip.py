"""Resolve the visitor address behind proxies that this deployment controls."""

from ipaddress import ip_address

from django.conf import settings
from django.http import HttpRequest

# Gunicorn reports an empty peer address for unix-socket connections.
UNIX_SOCKET_PEER = ""


def client_ip(request: HttpRequest) -> str:
    """Return the nearest untrusted hop, never a client-chosen leftmost value."""
    address = request.META.get("REMOTE_ADDR", "")
    trusted = settings.TRUSTED_PROXIES
    if address not in trusted:
        return address
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
    return address
