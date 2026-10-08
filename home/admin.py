from django.contrib import admin
from .models import (SocialMedia, PersonalInfo, Skill,
                     Interest, Testimonial, InformationCounter, Education, Experience,
                     Service,Category,Project,ProjectImage,ProjectVideo,Contact,
                     EngineeringChallenge, ExperienceBullet, ProjectMetric, Article)
# Register your models here.
admin.site.register(SocialMedia)
admin.site.register(PersonalInfo)
admin.site.register(Interest)
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'designation', 'consent_to_publish', 'is_published')
    list_filter = ('consent_to_publish', 'is_published')
    search_fields = ('client_name', 'review')

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
        (None, {'fields': ('category', 'name', 'slug', 'short_desc', 'description', 'features', 'work_type', 'technologies')}),
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
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'notification_status', 'created_at')
    list_filter = ('status', 'notification_status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'notification_status')
    list_editable = ('status',)
    actions = ('mark_read', 'mark_replied', 'retry_notifications')

    @admin.action(description='Mark selected enquiries as read')
    def mark_read(self, request, queryset):
        queryset.update(status='read')

    @admin.action(description='Mark selected enquiries as replied')
    def mark_replied(self, request, queryset):
        queryset.update(status='replied')

    @admin.action(description='Retry failed email notifications')
    def retry_notifications(self, request, queryset):
        from .notifications import notify_contact
        count = sum(notify_contact(item) == 'sent' for item in queryset.filter(notification_status='failed'))
        self.message_user(request, f'{count} notifications sent.')




@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'is_published', 'published_at')
    list_filter = ('is_published', 'topic')
    search_fields = ('title', 'title_bn', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
