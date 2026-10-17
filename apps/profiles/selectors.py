from django.db.models import QuerySet

from .models import Education, Experience, Interest, PersonalInfo, Skill, SocialMedia


def personal_info_get() -> PersonalInfo | None:
    return PersonalInfo.objects.order_by("pk").first()


def social_media_list() -> QuerySet[SocialMedia]:
    return SocialMedia.objects.all()


def experience_list() -> QuerySet[Experience]:
    return Experience.objects.prefetch_related("bullets").order_by("-id")


def education_list() -> QuerySet[Education]:
    return Education.objects.order_by("-id")


def skill_list() -> QuerySet[Skill]:
    return Skill.objects.all()


def interest_list() -> QuerySet[Interest]:
    return Interest.objects.all()
