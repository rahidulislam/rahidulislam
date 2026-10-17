from django.contrib import admin

from .models import (
    Education,
    Experience,
    ExperienceBullet,
    Interest,
    PersonalInfo,
    Skill,
    SocialMedia,
)


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 1
    fields = ("text", "order")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "value", "order")
    list_editable = ("group", "value", "order")
    search_fields = ("name", "group")
    ordering = ("group", "order", "name")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("designation", "company", "start_year", "end_year")
    readonly_fields = ("slug",)
    search_fields = ("designation", "company", "description")
    inlines = (ExperienceBulletInline,)


admin.site.register(SocialMedia)
admin.site.register(PersonalInfo)
admin.site.register(Interest)
admin.site.register(Education)
admin.site.register(ExperienceBullet)
