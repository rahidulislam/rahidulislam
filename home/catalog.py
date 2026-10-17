"""Compatibility imports; new code must use the domain module."""

from apps.projects.catalog import filter_catalog, project_card

__all__ = ["project_card", "filter_catalog"]
