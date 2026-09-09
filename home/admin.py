from django.contrib import admin
from .models import (SocialMedia, PersonalInfo, Skill,
                     Interest, Testimonial, InformationCounter, Education, Experience,
                     Service,Category,Project,ProjectImage,ProjectVideo,Contact)
# Register your models here.
admin.site.register(SocialMedia)
admin.site.register(PersonalInfo)
admin.site.register(Skill)
admin.site.register(Interest)
admin.site.register(Testimonial)
admin.site.register(InformationCounter)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Service)
admin.site.register(Category)
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


class ProjectVideoInline(admin.TabularInline):
    model = ProjectVideo
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'order')
    search_fields = ('name', 'short_desc', 'description', 'client_name')
    list_filter = ('category', 'is_published', 'is_featured')
    ordering = ('order', '-date', '-pk')
    fieldsets = (
        (None, {'fields': ('category', 'name', 'short_desc', 'description', 'features')}),
        ('Case study', {'fields': ('problem', 'contribution', 'technical_decisions', 'outcome', 'lessons')}),
        ('Links and media', {'fields': ('url', 'repository_url', 'image')}),
        ('Publishing', {'fields': ('is_published', 'is_featured', 'order')}),
        ('Client', {'fields': ('client_name', 'date')}),
    )
    inlines = (ProjectImageInline, ProjectVideoInline)

    @admin.display(description='Status', ordering='is_published')
    def status(self, obj):
        return 'Published' if obj.is_published else 'Draft'


admin.site.register(ProjectVideo)
admin.site.register(Contact)
