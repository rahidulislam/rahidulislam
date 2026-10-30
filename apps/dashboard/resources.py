"""Explicit presentation/form allowlist; persistence stays in each domain."""

from collections.abc import Callable
from dataclasses import dataclass

from django import forms
from django.db.models import Model
from django.forms import ModelForm, modelform_factory

from apps.articles import services as articles
from apps.articles.models import Article
from apps.contacts import services as contacts
from apps.contacts.models import PublicContact
from apps.portfolio import services as portfolio
from apps.portfolio.models import InformationCounter, Service, SiteBranding, Testimonial
from apps.profiles import services as profiles
from apps.profiles.models import (
    Education,
    Experience,
    ExperienceBullet,
    Interest,
    PersonalInfo,
    Skill,
    SocialMedia,
)
from apps.projects import services as projects
from apps.projects.models import (
    Category,
    EngineeringChallenge,
    Project,
    ProjectImage,
    ProjectMetric,
    ProjectVideo,
)


@dataclass(frozen=True)
class Resource:
    key: str
    label: str
    group: str
    model: type[Model]
    fields: tuple[str, ...]
    columns: tuple[str, ...]
    search: tuple[str, ...]
    save: Callable[..., Model]
    delete: Callable[..., None]
    parent: str = ""
    singleton: bool = False
    deletable: bool = True

    def form_class(self) -> type[ModelForm]:
        widgets = {}
        for name in self.fields:
            field = self.model._meta.get_field(name)
            if field.get_internal_type() == "DateField":
                widgets[name] = forms.DateInput(
                    attrs={"type": "date"}, format="%Y-%m-%d"
                )
            elif field.get_internal_type() == "TextField":
                widgets[name] = forms.Textarea(attrs={"rows": 5})
        return modelform_factory(self.model, fields=self.fields, widgets=widgets)


RESOURCES = (
    Resource(
        "site-branding",
        "Site branding",
        "Site content",
        SiteBranding,
        ("brand_name", "logo", "logo_dark", "site_icon"),
        ("brand_name", "updated_at"),
        ("brand_name",),
        portfolio.save_content,
        portfolio.delete_content,
        singleton=True,
        deletable=False,
    ),
    Resource(
        "projects",
        "Projects",
        "Projects",
        Project,
        (
            "category",
            "name",
            "slug",
            "short_desc",
            "description",
            "features",
            "work_type",
            "technologies",
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
            "url",
            "repository_url",
            "api_docs_url",
            "image",
            "is_published",
            "is_featured",
            "order",
            "client_name",
            "date",
        ),
        ("name", "category", "is_published", "order"),
        ("name", "short_desc"),
        projects.save_content,
        projects.delete_content,
    ),
    Resource(
        "categories",
        "Categories",
        "Projects",
        Category,
        ("name",),
        ("name",),
        ("name",),
        projects.save_content,
        projects.delete_content,
    ),
    Resource(
        "project-images",
        "Project images",
        "Projects",
        ProjectImage,
        ("project", "image", "kind", "alt_text", "caption", "order"),
        ("project", "caption", "kind", "order"),
        ("caption", "project__name"),
        projects.save_content,
        projects.delete_content,
        parent="project",
    ),
    Resource(
        "project-videos",
        "Project videos",
        "Projects",
        ProjectVideo,
        ("project", "file", "caption", "order"),
        ("project", "caption", "order"),
        ("caption", "project__name"),
        projects.save_content,
        projects.delete_content,
        parent="project",
    ),
    Resource(
        "challenges",
        "Engineering challenges",
        "Projects",
        EngineeringChallenge,
        (
            "project",
            "title",
            "problem",
            "approach",
            "solution",
            "trade_offs",
            "verification",
            "source_url",
            "is_published",
            "order",
        ),
        ("title", "project", "is_published"),
        ("title", "project__name"),
        projects.save_content,
        projects.delete_content,
        parent="project",
    ),
    Resource(
        "metrics",
        "Project metrics",
        "Projects",
        ProjectMetric,
        (
            "project",
            "label",
            "value",
            "explanation",
            "source_url",
            "is_published",
            "order",
        ),
        ("label", "value", "project", "is_published"),
        ("label", "project__name"),
        projects.save_content,
        projects.delete_content,
        parent="project",
    ),
    Resource(
        "articles",
        "Articles",
        "Articles",
        Article,
        (
            "title",
            "title_bn",
            "slug",
            "topic",
            "cover_image",
            "image_alt",
            "image_caption",
            "summary",
            "summary_bn",
            "body",
            "body_bn",
            "source_url",
            "is_published",
            "published_at",
        ),
        ("title", "topic", "is_published", "published_at"),
        ("title", "title_bn", "topic"),
        articles.save_content,
        articles.delete_content,
    ),
    Resource(
        "profile",
        "Personal profile",
        "Profile",
        PersonalInfo,
        (
            "name",
            "profession",
            "short_bio",
            "bio",
            "dob",
            "phone",
            "email",
            "is_available",
            "address",
            "website",
            "last_degree",
            "age",
            "image",
        ),
        ("name", "profession", "is_available"),
        ("name",),
        profiles.save_content,
        profiles.delete_content,
    ),
    Resource(
        "experiences",
        "Experience",
        "Profile",
        Experience,
        ("designation", "company", "start_year", "end_year", "description", "address"),
        ("designation", "company", "start_year", "end_year"),
        ("designation", "company"),
        profiles.save_content,
        profiles.delete_content,
    ),
    Resource(
        "experience-bullets",
        "Experience details",
        "Profile",
        ExperienceBullet,
        ("experience", "text", "order"),
        ("experience", "text", "order"),
        ("text", "experience__company"),
        profiles.save_content,
        profiles.delete_content,
        parent="experience",
    ),
    Resource(
        "education",
        "Education",
        "Profile",
        Education,
        (
            "degree_name",
            "institute",
            "start_year",
            "end_year",
            "description",
            "address",
        ),
        ("degree_name", "institute", "end_year"),
        ("degree_name", "institute"),
        profiles.save_content,
        profiles.delete_content,
    ),
    Resource(
        "skills",
        "Skills",
        "Profile",
        Skill,
        ("name", "value", "group", "order"),
        ("name", "value", "group", "order"),
        ("name", "group"),
        profiles.save_content,
        profiles.delete_content,
    ),
    Resource(
        "interests",
        "Interests",
        "Profile",
        Interest,
        ("name", "icon_name", "icon_color"),
        ("name", "icon_name"),
        ("name",),
        profiles.save_content,
        profiles.delete_content,
    ),
    Resource(
        "social-links",
        "Social links",
        "Profile",
        SocialMedia,
        ("name", "social_link"),
        ("name", "social_link"),
        ("name",),
        profiles.save_content,
        profiles.delete_content,
    ),
    Resource(
        "services",
        "Services",
        "Site content",
        Service,
        ("name", "icon_name", "description"),
        ("name", "description"),
        ("name",),
        portfolio.save_content,
        portfolio.delete_content,
    ),
    Resource(
        "testimonials",
        "Testimonials",
        "Site content",
        Testimonial,
        (
            "client_name",
            "designation",
            "review",
            "image",
            "consent_to_publish",
            "is_published",
        ),
        ("client_name", "consent_to_publish", "is_published"),
        ("client_name", "review"),
        portfolio.save_content,
        portfolio.delete_content,
    ),
    Resource(
        "counters",
        "Information counters",
        "Site content",
        InformationCounter,
        ("happy_client", "project", "support", "awards"),
        ("happy_client", "project", "support", "awards"),
        (),
        portfolio.save_content,
        portfolio.delete_content,
    ),
    Resource(
        "contact-details",
        "Contact details",
        "Site content",
        PublicContact,
        ("email", "phone", "whatsapp", "telegram", "location", "github", "linkedin"),
        ("email", "phone", "location"),
        ("email", "location"),
        contacts.save_content,
        contacts.delete_content,
        singleton=True,
        deletable=False,
    ),
)
RESOURCE_MAP = {resource.key: resource for resource in RESOURCES}
