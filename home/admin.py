from django.contrib import admin
from .models import (SocialMedia, PersonalInfo, Skill,
                     Interest, Testimonial, InformationCounter, Education, Experience,
                     Service,Category,Project,ProjectImage,ProjectVideo,Contact,
                     EngineeringChallenge, ExperienceBullet, ProjectMetric)
# Register your models here.
admin.site.register(SocialMedia)
admin.site.register(PersonalInfo)
admin.site.register(Interest)
admin.site.register(Testimonial)
admin.site.register(InformationCounter)
admin.site.register(Education)
admin.site.register(Service)
admin.site.register(Category)
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'kind', 'alt_text', 'caption', 'order')


class ProjectVideoInline(admin.TabularInline):
    model = ProjectVideo
    extra = 1


class EngineeringChallengeInline(admin.StackedInline):
    model = EngineeringChallenge
    extra = 0
    fields = ('title', 'problem', 'approach', 'solution', 'trade_offs', 'verification',
              'source_url', 'is_published', 'order')


class ProjectMetricInline(admin.TabularInline):
    model = ProjectMetric
    extra = 0
    fields = ('label', 'value', 'explanation', 'source_url', 'is_published', 'order')


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 1
    fields = ('text', 'order')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'value', 'order')
    list_editable = ('group', 'value', 'order')
    search_fields = ('name', 'group')
    ordering = ('group', 'order', 'name')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('designation', 'company', 'start_year', 'end_year')
    search_fields = ('designation', 'company', 'description')
    inlines = (ExperienceBulletInline,)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'order')
    search_fields = ('name', 'short_desc', 'description', 'client_name', 'project_type',
                     'project_role', 'collaboration', 'development_status',
                     'contribution_areas', 'constraints', 'validation')
    list_filter = ('category', 'is_published', 'is_featured')
    ordering = ('order', '-date', '-pk')
    fieldsets = (
        (None, {'fields': ('category', 'name', 'slug', 'short_desc', 'description', 'features')}),
        ('Case study', {'fields': ('project_type', 'project_role', 'collaboration',
                                   'development_status', 'contribution_areas', 'problem',
                                   'contribution', 'constraints', 'architecture_summary',
                                   'technical_decisions', 'validation', 'outcome', 'lessons')}),
        ('Links and media', {'fields': ('url', 'repository_url', 'api_docs_url', 'image')}),
        ('Publishing', {'fields': ('is_published', 'is_featured', 'order')}),
        ('Client', {'fields': ('client_name', 'date')}),
    )
    inlines = (ProjectImageInline, ProjectVideoInline, EngineeringChallengeInline, ProjectMetricInline)

    @admin.display(description='Status', ordering='is_published')
    def status(self, obj):
        return 'Published' if obj.is_published else 'Draft'


admin.site.register(ProjectVideo)
admin.site.register(EngineeringChallenge)
admin.site.register(ProjectMetric)
admin.site.register(ExperienceBullet)
admin.site.register(Contact)
