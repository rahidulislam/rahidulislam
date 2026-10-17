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
