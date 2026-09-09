import json
from pathlib import Path

from django.views.generic import DetailView, FormView, TemplateView
from .models import (InformationCounter, Interest, SocialMedia,
                     PersonalInfo, Skill, Testimonial, Education, Experience, Service,
                     Category, Project)
from .forms import ContactForm
from django.contrib import messages
from .portfolio_content import backend_skills, fallback_experiences, fallback_projects

# Create your views here.
class HomeView(FormView):
    form_class = ContactForm
    template_name = "home/index.html"
    success_url = "/#contact"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['skills'] = Skill.objects.all()
        data['backend_skills'] = list(data['skills']) or backend_skills
        data['interests'] = Interest.objects.all()
        data['testimonials'] = Testimonial.objects.all()
        data['counter'] = InformationCounter.objects.first()
        data['educations'] = Education.objects.all().order_by('-id')
        data['experiences'] = Experience.objects.exclude(company__iexact='TalentBridge', designation__iexact='Mid Level Python Developer').order_by('-id')
        data['fallback_experiences'] = fallback_experiences
        data['services'] = Service.objects.all()
        data['categories'] = Category.objects.all()
        data['projects'] = Project.objects.select_related('category').all()
        data['fallback_projects'] = fallback_projects
        from .portfolio_data import get_portfolio_data
        data.update(get_portfolio_data())
        data['contact_profile'] = data['cv_profile']
        data['home_preview'] = True
        featured = [project for project in data['projects'] if project.is_featured]
        data['projects'] = (featured or data['projects'])[:3]
        data['fallback_projects'] = data['fallback_projects'][:3]
        return data

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, "Your message was saved. Thank you!")
        return super().form_valid(form)


class ProjectDetailView(DetailView):
    queryset = Project.objects.filter(is_published=True).select_related('category').prefetch_related('project_image', 'videos')
    template_name = "home/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['social_items'] = SocialMedia.objects.all()
        data['personal_info'] = PersonalInfo.objects.first()
        return data


class CaseStudyView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        from django.http import Http404
        from django.shortcuts import redirect
        item = next((item for item in fallback_projects if item['slug'] == kwargs['slug']), None)
        if item:
            project = Project.objects.filter(name__iexact=item['name']).first()
            if project:
                if not project.is_published:
                    raise Http404('Project not found')
                return redirect('home:project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)

    template_name = "home/case_study.html"

    def get_context_data(self, **kwargs):
        from django.http import Http404
        data = super().get_context_data(**kwargs)
        project = next((item for item in fallback_projects if item["slug"] == self.kwargs["slug"]), None)
        if project is None:
            raise Http404("Project not found")
        data.update(project=project, personal_info=PersonalInfo.objects.first(), social_items=SocialMedia.objects.all())
        return data


def download_cv(request):
    """Generate from the same live content used by the portfolio."""
    from io import BytesIO
    from django.http import FileResponse, HttpResponseNotAllowed
    from .cv_pdf import build_cv
    from .portfolio_data import get_portfolio_data
    if request.method not in ("GET", "HEAD"):
        return HttpResponseNotAllowed(["GET", "HEAD"])
    data = get_portfolio_data()
    response = FileResponse(BytesIO(build_cv(data['cv_profile'], data['cv_projects'])),
                            as_attachment=True, filename='Rahidul_Islam_Python_Developer_CV.pdf',
                            content_type='application/pdf')
    response['Cache-Control'] = 'no-store'
    return response


class ProjectListView(TemplateView):
    template_name = 'home/projects.html'

    def get_context_data(self, **kwargs):
        from .portfolio_data import get_portfolio_data
        data = super().get_context_data(**kwargs)
        data.update(get_portfolio_data())
        data['categories'] = Category.objects.filter(project_category__is_published=True).distinct()
        data['project_index'] = True
        return data
