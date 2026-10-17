from django.db.models import QuerySet

from .models import Category, Project


def published_projects() -> QuerySet[Project]:
    return Project.objects.filter(is_published=True).select_related("category")


def project_by_slug(*, slug: str) -> Project | None:
    return (
        published_projects()
        .filter(slug=slug)
        .prefetch_related(
            "project_image", "videos", "engineering_challenges", "metrics"
        )
        .first()
    )


def project_by_pk(*, pk: int) -> Project | None:
    return published_projects().filter(pk=pk).first()


def project_names() -> set[str]:
    return {name.casefold() for name in Project.objects.values_list("name", flat=True)}


def project_name_is_private(*, name: str) -> bool:
    return Project.objects.filter(name__iexact=name, is_published=False).exists()


def published_categories() -> QuerySet[Category]:
    return Category.objects.filter(project_category__is_published=True).distinct()
