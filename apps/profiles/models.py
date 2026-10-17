from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class SocialMedia(models.Model):
    name = models.CharField(max_length=20)
    social_link = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "home_socialmedia"


class PersonalInfo(models.Model):
    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=50)
    short_bio = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    dob = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_available = models.BooleanField(default=True)
    address = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    last_degree = models.CharField(max_length=50, blank=True)
    age = models.IntegerField()
    image = models.ImageField(upload_to="images/", blank=True)

    def __str__(self) -> str:
        return self.name

    def get_image_url(self):
        return self.image.url if self.image else None

    class Meta:
        db_table = "home_personalinfo"


class Skill(models.Model):
    name = models.CharField(max_length=50)
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    group = models.CharField(max_length=50, default="Core")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "home_skill"
        ordering = ["group", "order", "name", "pk"]

    def __str__(self):
        return self.name


class Interest(models.Model):
    name = models.CharField(max_length=50)
    icon_name = models.CharField(max_length=50)
    icon_color = models.CharField(max_length=7)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "home_interest"


class Education(models.Model):
    degree_name = models.CharField(max_length=50)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10)
    description = models.TextField()
    institute = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.degree_name

    class Meta:
        db_table = "home_education"


class Experience(models.Model):
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    designation = models.CharField(max_length=50)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10)
    description = models.TextField()
    company = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.designation

    def save(self, *args, **kwargs):
        if not self.slug:
            from .experience_slugs import reserved_experience_slugs

            reserved = reserved_experience_slugs(self.company)
            base = slugify(self.company) or "experience"
            candidate = base[:120]
            suffix = 2
            while (
                candidate in reserved
                or Experience.objects.exclude(pk=self.pk)
                .filter(slug=candidate)
                .exists()
            ):
                suffix_text = f"-{suffix}"
                candidate = f"{base[:120 - len(suffix_text)]}{suffix_text}"
                suffix += 1
            self.slug = candidate
            if kwargs.get("update_fields"):
                kwargs["update_fields"] = set(kwargs["update_fields"]) | {"slug"}
        super().save(*args, **kwargs)

    class Meta:
        db_table = "home_experience"


class ExperienceBullet(models.Model):
    experience = models.ForeignKey(
        Experience, on_delete=models.CASCADE, related_name="bullets"
    )
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "home_experiencebullet"
        ordering = ["order", "pk"]

    def __str__(self):
        return f"{self.experience}: {self.text[:60]}"
