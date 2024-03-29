from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from tinymce.models import HTMLField
# Create your models here.


class SocialMedia(models.Model):
    name = models.CharField(max_length=20)
    social_link = models.URLField()

    def __str__(self):
        return self.name


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
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self) -> str:
        return self.name

    def get_image_url(self):
        return self.image.url if self.image else None


class InformationCounter(models.Model):
    happy_client = models.PositiveIntegerField()
    project = models.PositiveIntegerField()
    support = models.PositiveIntegerField()
    awards = models.PositiveIntegerField()

    def __str__(self):
        return str(self.happy_client)


class Skill(models.Model):
    name = models.CharField(max_length=50)
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.name


class Interest(models.Model):
    name = models.CharField(max_length=50)
    icon_name = models.CharField(max_length=50)
    icon_color = models.CharField(max_length=7)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=50)
    review = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.client_name


class Education(models.Model):
    degree_name = models.CharField(max_length=50)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10)
    description = HTMLField()
    institute = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.degree_name


class Experience(models.Model):
    designation = models.CharField(max_length=50)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10)
    description = HTMLField()
    company = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.designation


class Service(models.Model):
    name = models.CharField(max_length=50)
    icon_name = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Project(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='project_category')
    name = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', blank=True)
    url = models.URLField(blank=True)
    client_name = models.CharField(max_length=100)
    date = models.DateField()
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.name

    def get_image_url(self):
        return self.image.url if self.image else None


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='project_image')
    image = models.ImageField(upload_to='project/', blank=True)

    def __str__(self):
        return self.project.name

    def get_image_url(self):
        return self.image.url if self.image else None


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.email
