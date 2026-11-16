"""Limit failed password attempts on every login surface (admin and dashboard)."""

import hashlib
import logging

from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from .client_ip import client_ip

logger = logging.getLogger(__name__)

WINDOW_SECONDS = 15 * 60
# One visitor guessing one account, and one visitor spraying many accounts.
ACCOUNT_FAILURE_LIMIT = 5
ADDRESS_FAILURE_LIMIT = 20
THROTTLED_MESSAGE = "Too many failed sign-in attempts. Try again in 15 minutes."


def _keys(address: str, username: str) -> tuple[tuple[str, int], ...]:
    # Hash identifiers so cache keys never store raw usernames or addresses.
    account = hashlib.sha256(f"{address}\n{username.lower()}".encode()).hexdigest()
    origin = hashlib.sha256(address.encode()).hexdigest()
    return (
        (f"login-fail:account:{account}", ACCOUNT_FAILURE_LIMIT),
        (f"login-fail:address:{origin}", ADDRESS_FAILURE_LIMIT),
    )


def is_throttled(*, address: str, username: str) -> bool:
    try:
        return any(
            (cache.get(key) or 0) >= limit for key, limit in _keys(address, username)
        )
    except DatabaseError:
        logger.warning("Login throttle cache unavailable; attempt allowed.")
        return False


def record_failure(*, address: str, username: str) -> None:
    try:
        for key, _ in _keys(address, username):
            cache.add(key, 0, WINDOW_SECONDS)
            try:
                cache.incr(key)
            except ValueError:  # The window expired between add() and incr().
                cache.set(key, 1, WINDOW_SECONDS)
    except DatabaseError:
        logger.warning("Login throttle cache unavailable; failure not recorded.")


def clear_account(*, address: str, username: str) -> None:
    try:
        cache.delete(_keys(address, username)[0][0])
    except DatabaseError:
        logger.warning("Login throttle cache unavailable; counter not cleared.")


class ThrottledLoginMixin(AuthenticationForm):
    """Reject throttled attempts before authenticating and count each failure."""

    def clean(self):
        address = client_ip(self.request) if self.request else ""
        username = self.data.get("username", "")[:150]
        if is_throttled(address=address, username=username):
            raise ValidationError(THROTTLED_MESSAGE, code="throttled")
        try:
            cleaned = super().clean()
        except ValidationError:
            record_failure(address=address, username=username)
            raise
        clear_account(address=address, username=username)
        return cleaned
