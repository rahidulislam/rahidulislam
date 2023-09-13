from django.views.generic import DetailView, FormView
from .models import (InformationCounter, Interest, SocialMedia,
                     PersonalInfo, Skill, Testimonial, Education, Experience, Service,
                     Category, Project)
from .forms import ContactForm
from django.contrib import messages

# Create your views here.
class HomeView(FormView):
    form_class = ContactForm
    template_name = "home/index.html"
    success_url = "."

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['social_items'] = SocialMedia.objects.all()
        data['personal_info'] = PersonalInfo.objects.first()
        data['skills'] = Skill.objects.all()
        data['interests'] = Interest.objects.all()
        data['testimonials'] = Testimonial.objects.all()
        data['counter'] = InformationCounter.objects.first()
        data['educations'] = Education.objects.all().order_by('-id')
        data['experiences'] = Experience.objects.all().order_by('-id')
        data['services'] = Service.objects.all()
        categories = Category.objects.all()[:7]
        data['categories'] = categories
        data['projects'] = Project.objects.filter(category__in=categories)
        return data

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, "Your message has been sent. Thank you!")
        return super().form_valid(form)


class ProjectDetailView(DetailView):
    queryset = Project.objects.prefetch_related('project_image')
    template_name = "home/project_detail.html"
    context_object_name = "project"
