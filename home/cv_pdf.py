"""Compatibility imports; new code must use the domain module."""

from apps.resumes.pdf import build_cv

__all__ = ["build_cv"]
