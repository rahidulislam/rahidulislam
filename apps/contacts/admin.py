from django.contrib import admin

from .models import Contact, PublicContact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "subject",
        "status",
        "notification_status",
        "created_at",
    )
    list_filter = ("status", "notification_status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "notification_status")
    list_editable = ("status",)
    actions = ("mark_read", "mark_replied", "retry_notifications")

    @admin.action(description="Mark selected enquiries as read")
    def mark_read(self, request, queryset):
        from .services import mark_enquiries

        mark_enquiries(enquiries=queryset, status="read")

    @admin.action(description="Mark selected enquiries as replied")
    def mark_replied(self, request, queryset):
        from .services import mark_enquiries

        mark_enquiries(enquiries=queryset, status="replied")

    @admin.action(description="Retry failed email notifications")
    def retry_notifications(self, request, queryset):
        from .services import retry_notifications

        count = retry_notifications(enquiries=queryset)
        self.message_user(request, f"{count} notifications sent.")


@admin.register(PublicContact)
class PublicContactAdmin(admin.ModelAdmin):
    list_display = ("__str__", "email", "phone", "whatsapp", "telegram")
    fieldsets = (
        (
            "Contact",
            {
                "fields": ("email", "phone", "whatsapp", "telegram", "location"),
                "description": "Shown in the footer on every page and in the homepage contact section. Leave a field blank to hide it.",
            },
        ),
        ("Professional profiles", {"fields": ("github", "linkedin")}),
    )

    def has_add_permission(self, request):
        return (
            super().has_add_permission(request) and not PublicContact.objects.exists()
        )

    def has_delete_permission(self, request, obj=None):
        return False
