"""CV composition reuses profile and project contracts without HTTP dependencies."""

from typing import Any

from apps.profiles.presentation import profile_context
from apps.projects.presentation import project_context


def resume_context() -> dict[str, Any]:
    data = {**profile_context(), **project_context()}
    data["cv_projects"] = data["fallback_projects"] + [
        {
            "name": item.name,
            "category": item.category.name,
            "short_desc": item.short_desc,
            "technical_notes": item.features.splitlines(),
        }
        for item in data["projects"]
    ]
    return data
