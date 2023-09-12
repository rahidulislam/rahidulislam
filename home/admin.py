from django.contrib import admin
from .models import (SocialMedia, PersonalInfo, Skill,
                     Interest, Testimonial, InformationCounter, Education, Experience,
                     Service,Category,Project,ProjectImage)
# Register your models here.
admin.site.register(SocialMedia)
admin.site.register(PersonalInfo)
admin.site.register(Skill)
admin.site.register(Interest)
admin.site.register(Testimonial)
admin.site.register(InformationCounter)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Service)
admin.site.register(Category)
admin.site.register(Project)
admin.site.register(ProjectImage)

