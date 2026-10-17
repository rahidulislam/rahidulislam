"""Compatibility entry point for external CV export scripts."""

from apps.resumes.presentation import resume_context

get_portfolio_data = resume_context
__all__ = ["get_portfolio_data"]
