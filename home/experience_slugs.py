"""Compatibility imports; new code must use the domain module."""

from apps.profiles.experience_slugs import (
    FALLBACK_SLUGS,
    experience_identity,
    reserved_experience_slugs,
)

__all__ = ["experience_identity", "reserved_experience_slugs", "FALLBACK_SLUGS"]
