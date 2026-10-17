"""Legacy imports retained for historical migrations and external scripts."""

from apps.articles.models import Article
from apps.contacts.models import Contact, PublicContact
from apps.portfolio.models import InformationCounter, Service, Testimonial
from apps.profiles.models import (
    Education,
    Experience,
    ExperienceBullet,
    Interest,
    PersonalInfo,
    Skill,
    SocialMedia,
)
from apps.projects.models import (
    Category,
    EngineeringChallenge,
    Project,
    ProjectImage,
    ProjectMetric,
    ProjectVideo,
    validate_video_size,
)

__all__ = [
    "SocialMedia",
    "PersonalInfo",
    "Skill",
    "Interest",
    "Education",
    "Experience",
    "ExperienceBullet",
    "Category",
    "Project",
    "ProjectImage",
    "EngineeringChallenge",
    "ProjectMetric",
    "ProjectVideo",
    "Article",
    "PublicContact",
    "Contact",
    "InformationCounter",
    "Testimonial",
    "Service",
    "validate_video_size",
]
