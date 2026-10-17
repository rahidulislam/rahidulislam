from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    from .forms import ArticleForm

    form = ArticleForm
    fieldsets = (
        ("Article", {"fields": ("title", "title_bn", "slug", "topic")}),
        ("Cover image", {"fields": ("cover_image", "image_alt", "image_caption")}),
        ("Introduction", {"fields": ("summary", "summary_bn")}),
        ("Content", {"fields": ("body", "body_bn")}),
        ("Publication", {"fields": ("source_url", "is_published", "published_at")}),
    )

    def get_urls(self):
        from django.urls import path

        return [
            path(
                "preview/",
                self.admin_site.admin_view(self.preview),
                name="articles_article_preview",
            )
        ] + super().get_urls()

    def preview(self, request):
        from django.http import JsonResponse

        from .rendering import render_article

        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)
        if not (
            self.has_add_permission(request) or self.has_change_permission(request)
        ):
            return JsonResponse({"error": "Permission denied"}, status=403)
        return JsonResponse(
            {"html": render_article(request.POST.get("body", "")[:200000])}
        )

    list_display = ("title", "topic", "is_published", "published_at")
    list_filter = ("is_published", "topic")
    search_fields = ("title", "title_bn", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
