from django.db import models
from django.templatetags.static import static


class Article(models.Model):
    title = models.CharField(max_length=180)
    title_bn = models.CharField(max_length=180, blank=True)
    slug = models.SlugField(max_length=180, unique=True)
    summary = models.TextField()
    summary_bn = models.TextField(blank=True)
    body = models.TextField(
        help_text="Markdown: headings, bold, lists, links, images and fenced code. HTML is escaped."
    )
    body_bn = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="articles/covers/", blank=True)
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="Describe the cover image for screen readers.",
    )
    image_caption = models.CharField(max_length=240, blank=True)
    topic = models.CharField(max_length=80)
    source_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateField(blank=True, null=True)

    @property
    def reading_minutes(self):
        import math

        return max(
            1, math.ceil(max(len(self.body.split()), len(self.body_bn.split())) / 200)
        )

    @property
    def cover_url(self):
        return (
            self.cover_image.url
            if self.cover_image
            else static("img/articles/engineering-notes.svg")
        )

    class Meta:
        db_table = "home_article"
        ordering = ["-published_at", "-pk"]

    def __str__(self):
        return self.title
