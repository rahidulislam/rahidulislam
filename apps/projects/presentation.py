"""Compose managed projects with the source-backed fallback catalog."""

from pathlib import Path
from typing import Any

from django.conf import settings
from django.http import Http404

from apps.profiles.selectors import personal_info_get, social_media_list

from .content import fallback_projects
from .madrasha_content import MADRASHA_SCREENSHOTS
from .selectors import (
    project_by_slug,
    project_name_is_private,
    project_names,
    published_projects,
)
from .showcase import PROJECT_SHOWCASES


def project_context() -> dict[str, Any]:
    projects = list(published_projects())
    existing_names = project_names()
    curated = [
        item
        for item in fallback_projects
        if item["name"].casefold() not in existing_names
    ]
    return {"projects": projects, "fallback_projects": curated}


def case_study_context(*, slug: str) -> dict[str, Any]:
    data = {}
    asset = f"img/architecture/{slug}.svg"
    data["architecture_asset"] = (
        asset if (Path(settings.BASE_DIR) / "static" / asset).is_file() else ""
    )
    showcase = PROJECT_SHOWCASES.get(slug, {})
    is_ilmora = slug == "ilmora-madrasha-management"
    data["static_screenshots"] = showcase.get(
        "screenshots", MADRASHA_SCREENSHOTS if is_ilmora else []
    )
    data["screenshots_description"] = (
        "Captured from the live Ilmora frontend using its browser-local demo data."
        if is_ilmora
        else "Application screenshots using synthetic demo data."
    )
    data["demo_video_asset"] = showcase.get(
        "video", "video/ilmora-demo.webm" if is_ilmora else ""
    )
    data["demo_video_type"] = "video/webm" if is_ilmora else "video/mp4"
    data["demo_video_poster"] = showcase.get(
        "poster", "img/projects/ilmora-dashboard.jpg"
    )
    data["demo_video_description"] = (
        "A short recording of Ilmora’s browser-local demo: landing, dashboard, students, attendance and fees."
        if is_ilmora
        else "A screenshot montage using synthetic demo data."
    )
    project = project_by_slug(slug=slug)
    if project:
        data.update(
            project=project,
            managed_project=True,
            published_challenges=[
                item
                for item in project.engineering_challenges.all()
                if item.is_published
            ],
            published_metrics=[
                item for item in project.metrics.all() if item.is_published
            ],
            architecture_images=[
                item
                for item in project.project_image.all()
                if item.kind == item.ARCHITECTURE
            ],
            screenshots=[
                item
                for item in project.project_image.all()
                if item.kind == item.SCREENSHOT
            ],
            personal_info=personal_info_get(),
            social_items=social_media_list(),
        )
        return data
    project = next((item for item in fallback_projects if item["slug"] == slug), None)
    if project is None or project_name_is_private(name=project["name"]):
        raise Http404("Project not found")
    data.update(
        project=project,
        personal_info=personal_info_get(),
        social_items=social_media_list(),
    )
    return data
