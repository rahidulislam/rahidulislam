from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.core.validators import FileExtensionValidator
from django.db import models


class InformationCounter(models.Model):
    happy_client = models.PositiveIntegerField()
    project = models.PositiveIntegerField()
    support = models.PositiveIntegerField()
    awards = models.PositiveIntegerField()

    def __str__(self):
        return str(self.happy_client)

    class Meta:
        db_table = "home_informationcounter"


class Testimonial(models.Model):
    consent_to_publish = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    client_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=50)
    review = models.TextField()
    image = models.ImageField(upload_to="images/", blank=True)

    def __str__(self):
        return self.client_name

    class Meta:
        db_table = "home_testimonial"


class Service(models.Model):
    name = models.CharField(max_length=50)
    icon_name = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "home_service"


def validate_brand_image_size(value: File) -> None:
    if value.size > 2 * 1024 * 1024:
        raise ValidationError("Brand images must be 2 MiB or smaller.")


class SiteBranding(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    brand_name = models.CharField(max_length=80, default="rahidul.")
    logo = models.ImageField(
        "Logo for light backgrounds",
        upload_to="branding/",
        blank=True,
        validators=[
            validate_brand_image_size,
            FileExtensionValidator(["png", "jpg", "jpeg", "webp"]),
        ],
        help_text="PNG, JPEG or WebP, up to 2 MiB. Use a tightly cropped image with readable lettering.",
    )
    logo_dark = models.ImageField(
        "Logo for dark backgrounds",
        upload_to="branding/",
        blank=True,
        validators=[
            validate_brand_image_size,
            FileExtensionValidator(["png", "jpg", "jpeg", "webp"]),
        ],
        help_text="Optional light-coloured logo for dark mode. If omitted, the regular logo uses a white backing for contrast.",
    )
    site_icon = models.ImageField(
        "Site icon",
        upload_to="branding/icons/",
        blank=True,
        validators=[
            validate_brand_image_size,
            FileExtensionValidator(["png", "jpg", "jpeg", "webp"]),
        ],
        help_text="Square PNG, JPEG or WebP, at least 32 × 32 pixels and up to 2 MiB. A 256 × 256 PNG is recommended.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site branding"
        verbose_name_plural = "Site branding"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(id=1), name="site_branding_singleton"
            )
        ]

    def __str__(self):
        return self.brand_name

    def clean(self):
        super().clean()
        if self.site_icon and (
            self.site_icon.width != self.site_icon.height
            or (self.site_icon.width or 0) < 32
        ):
            raise ValidationError(
                {"site_icon": "Use a square icon of at least 32 × 32 pixels."}
            )
