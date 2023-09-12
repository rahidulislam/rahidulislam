from django.contrib import admin
from .models import SocialMedia,PersonalInfo,Skill,Interest,Testimonial, InformationCounter
# Register your models here.
admin.site.register(SocialMedia)
admin.site.register(PersonalInfo)
admin.site.register(Skill)
admin.site.register(Interest)
admin.site.register(Testimonial)
admin.site.register(InformationCounter)