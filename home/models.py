from django.db import models

# Create your models here.
class SocialMedia(models.Model):
    name = models.CharField(max_length=20)
    social_link = models.URLField()

    def __str__(self):
        return self.name

# about section
# Personal Info-> profession, short_desc, desc, dob, phone, email, is_available, city, website, degree, age
# skill-> name, percentage
# interest -> interest name, icon name
# testimonial -> client name, designation, review, client image

#resume section
# education-> degree name, duration, details, institution_name, address
# experience -> designation, duration, details, company_name, address
# experience content-> company, bullet_point

# service
#service -> name, details, icon_name

# portfolio
# category -> category_name
# project -> project name, short_dec, image, url, client name, project date, project image for slider