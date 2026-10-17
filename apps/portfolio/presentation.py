"""Cross-domain homepage composition; domain apps do not import this module."""

from typing import Any

from apps.profiles.content import backend_skills, fallback_experiences
from apps.profiles.presentation import profile_context
from apps.profiles.selectors import experience_list, interest_list
from apps.projects.presentation import project_context
from apps.projects.selectors import published_categories

from .selectors import information_counter_get, published_testimonials, service_list


def homepage_context() -> dict[str, Any]:
    data = {**profile_context(), **project_context()}
    data.update(
        backend_skills=data["skills"] or backend_skills,
        experiences=experience_list().exclude(
            company__iexact="TalentBridge",
            designation__iexact="Mid Level Python Developer",
        ),
        interests=interest_list(),
        testimonials=published_testimonials(),
        counter=information_counter_get(),
        fallback_experiences=fallback_experiences,
        services=service_list(),
        categories=published_categories(),
        contact_profile=data["cv_profile"],
        home_preview=True,
    )
    selected_names = {
        "TalentBridge",
        "Smart Document Vault",
        "Ilmora — Madrasha Management",
    }
    data["fallback_projects"] = [
        item for item in data["fallback_projects"] if item["name"] in selected_names
    ]
    remaining_slots = max(0, 3 - len(data["fallback_projects"]))
    data["projects"] = [
        item for item in data["projects"] if item.name in selected_names
    ][:remaining_slots]
    return data
