from django.contrib import admin

from .models import InformationCounter, Service, Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "designation", "consent_to_publish", "is_published")
    list_filter = ("consent_to_publish", "is_published")
    search_fields = ("client_name", "review")


admin.site.register(InformationCounter)
admin.site.register(Service)
