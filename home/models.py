from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class SocialMedia(models.Model):
    name = models.CharField(max_length=20)
    social_link = models.URLField()

    def __str__(self):
        return self.name

# about section
# Personal Info-> profession, short_desc, desc, dob, phone, email, is_available, city, website, degree, age
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
    
class Skill(models.Model):
    name = models.CharField(max_length=50)
    value = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])



    def __str__(self):
        return self.name

# skill-> name, percentage
# interest -> interest name, icon name
# testimonial -> client name, designation, review, client image

# resume section
# education-> degree name, duration, details, institution_name, address
# experience -> designation, duration, details, company_name, address
# experience content-> company, bullet_point

# service
# service -> name, details, icon_name

# portfolio
# category -> category_name
# project -> project name, short_dec, image, url, client name, project date, project image for slider
