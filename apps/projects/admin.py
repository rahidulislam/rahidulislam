from django.contrib import admin

from .models import (
    Category,
    EngineeringChallenge,
    Project,
    ProjectImage,
    ProjectMetric,
    ProjectVideo,
)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "kind", "alt_text", "caption", "order")


class ProjectVideoInline(admin.TabularInline):
    model = ProjectVideo
    extra = 1


class EngineeringChallengeInline(admin.StackedInline):
    model = EngineeringChallenge
    extra = 0
    fields = (
        "title",
        "problem",
        "approach",
        "solution",
        "trade_offs",
        "verification",
        "source_url",
        "is_published",
        "order",
    )


class ProjectMetricInline(admin.TabularInline):
    model = ProjectMetric
    extra = 0
    fields = ("label", "value", "explanation", "source_url", "is_published", "order")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "order")
    search_fields = (
        "name",
        "short_desc",
        "description",
        "client_name",
        "project_type",
        "project_role",
        "collaboration",
        "development_status",
        "contribution_areas",
        "constraints",
        "validation",
    )
    list_filter = ("category", "is_published", "is_featured")
    ordering = ("order", "-date", "-pk")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "short_desc",
                    "description",
                    "features",
                    "work_type",
                    "technologies",
                )
            },
        ),
        (
            "Case study",
            {
                "fields": (
                    "project_type",
                    "project_role",
                    "collaboration",
                    "development_status",
                    "contribution_areas",
                    "problem",
                    "contribution",
                    "constraints",
                    "architecture_summary",
                    "technical_decisions",
                    "validation",
                    "outcome",
                    "lessons",
                )
            },
        ),
        (
            "Links and media",
            {"fields": ("url", "repository_url", "api_docs_url", "image")},
        ),
        ("Publishing", {"fields": ("is_published", "is_featured", "order")}),
        ("Client", {"fields": ("client_name", "date")}),
    )
    inlines = (
        ProjectImageInline,
        ProjectVideoInline,
        EngineeringChallengeInline,
        ProjectMetricInline,
    )

    @admin.display(description="Status", ordering="is_published")
    def status(self, obj):
        return "Published" if obj.is_published else "Draft"


admin.site.register(Category)
admin.site.register(ProjectVideo)
admin.site.register(EngineeringChallenge)
admin.site.register(ProjectMetric)
