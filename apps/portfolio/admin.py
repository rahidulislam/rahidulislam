from django.contrib import admin

from .models import InformationCounter, Service, SiteBranding, Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "designation", "consent_to_publish", "is_published")
    list_filter = ("consent_to_publish", "is_published")
    search_fields = ("client_name", "review")


admin.site.register(InformationCounter)
admin.site.register(Service)


@admin.register(SiteBranding)
class SiteBrandingAdmin(admin.ModelAdmin):
    fields = ("brand_name", "logo", "logo_dark", "site_icon")

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteBranding.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
