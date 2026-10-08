from django.views.generic import FormView, RedirectView, TemplateView
from django.http import HttpResponse
from django.urls import reverse
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request_language"] = self.request.COOKIES.get("portfolio_language", "en")
        kwargs["request_ip"] = self.request.META.get("REMOTE_ADDR", "unknown")
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['skills'] = Skill.objects.all()
        data['backend_skills'] = list(data['skills']) or backend_skills
        data['interests'] = Interest.objects.all()
        data['testimonials'] = Testimonial.objects.filter(consent_to_publish=True, is_published=True)
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
        selected_names = {'TalentBridge', 'Smart Document Vault', 'Ilmora — Madrasha Management'}
        data['fallback_projects'] = [
            project for project in data['fallback_projects']
            if project['name'] in selected_names
        ]
        remaining_slots = max(0, 3 - len(data['fallback_projects']))
        managed_selected = [
            project for project in data['projects']
            if project.is_published and project.name in selected_names
        ]
        data['projects'] = managed_selected[:remaining_slots]
        return data

    def form_valid(self, form):
        contact = form.save()
        from .notifications import notify_contact
        notify_contact(contact)
        messages.success(
            self.request, "Your message was saved. Thank you!")
        return super().form_valid(form)


class LegacyProjectDetailView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        from django.shortcuts import get_object_or_404
        project = get_object_or_404(Project, pk=kwargs['pk'], is_published=True)
        return reverse('home:case_study', args=[project.slug])


class CaseStudyView(TemplateView):
    template_name = "home/case_study.html"

    def get_context_data(self, **kwargs):
        from django.http import Http404
        data = super().get_context_data(**kwargs)
        from pathlib import Path
        from django.conf import settings
        slug = self.kwargs['slug']
        asset = f'img/architecture/{slug}.svg'
        data['architecture_asset'] = asset if (Path(settings.BASE_DIR) / 'static' / asset).is_file() else ''
        data['demo_video_asset'] = 'video/ilmora-demo.webm' if slug == 'ilmora-madrasha-management' else ''
        project = Project.objects.filter(slug=self.kwargs['slug'], is_published=True).select_related('category').prefetch_related('project_image', 'videos', 'engineering_challenges', 'metrics').first()
        if project:
            from .madrasha_content import MADRASHA_SCREENSHOTS
            data['static_screenshots'] = MADRASHA_SCREENSHOTS if project.slug == 'ilmora-madrasha-management' else []
            data.update(
                project=project,
                managed_project=True,
                published_challenges=[item for item in project.engineering_challenges.all() if item.is_published],
                published_metrics=[item for item in project.metrics.all() if item.is_published],
                architecture_images=[item for item in project.project_image.all() if item.kind == item.ARCHITECTURE],
                screenshots=[item for item in project.project_image.all() if item.kind == item.SCREENSHOT],
                personal_info=PersonalInfo.objects.first(), social_items=SocialMedia.objects.all(),
            )
            return data
        project = next((item for item in fallback_projects if item["slug"] == self.kwargs["slug"]), None)
        if project is None or Project.objects.filter(name__iexact=project['name'], is_published=False).exists():
            raise Http404("Project not found")
        from .madrasha_content import MADRASHA_SCREENSHOTS
        data['static_screenshots'] = MADRASHA_SCREENSHOTS if project['slug'] == 'ilmora-madrasha-management' else []
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


def sitemap_xml(request):
    from .models import Article
    from .portfolio_data import get_portfolio_data
    urls = [request.build_absolute_uri(reverse("home:home")), request.build_absolute_uri(reverse("home:projects"))]
    urls += [request.build_absolute_uri(reverse("home:case_study", args=[p.slug])) for p in Project.objects.filter(is_published=True).only("slug")]
    urls += [request.build_absolute_uri(reverse('home:articles')), request.build_absolute_uri(reverse('home:experience'))]
    urls += [request.build_absolute_uri(reverse('home:article_detail', args=[article.slug])) for article in Article.objects.filter(is_published=True).only('slug')]
    urls += [request.build_absolute_uri(reverse('home:experience_detail', args=[item['slug']])) for item in get_portfolio_data()['cv_profile']['experience']]
    body = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">" + "".join(f"<url><loc>{url}</loc></url>" for url in urls) + "</urlset>"
    return HttpResponse(body, content_type="application/xml")


def robots_txt(request):
    sitemap = request.build_absolute_uri(reverse("home:sitemap"))
    return HttpResponse(f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {sitemap}\n", content_type="text/plain")


class ProjectListView(TemplateView):
    template_name = 'home/projects.html'

    def get_context_data(self, **kwargs):
        from .portfolio_data import get_portfolio_data
        data = super().get_context_data(**kwargs)
        data.update(get_portfolio_data())
        data['categories'] = Category.objects.filter(project_category__is_published=True).distinct()
        data['project_index'] = True
        from .catalog import filter_catalog
        query = self.request.GET.get('q', '')[:200].strip()
        work_type = self.request.GET.get('type', '')
        technology = self.request.GET.get('technology', '')[:80]
        data['project_cards'], data['technologies'] = filter_catalog(data, query, work_type, technology)
        data.update(query=query, selected_type=work_type, selected_technology=technology)
        return data


class ContactFormView(HomeView):
    """Use the complete portfolio context for direct visits and validation errors."""


class ArticleListView(TemplateView):
    template_name = 'home/articles.html'

    def get_context_data(self, **kwargs):
        from .models import Article
        data = super().get_context_data(**kwargs)
        data['articles'] = Article.objects.filter(is_published=True)
        return data


class ArticleDetailView(TemplateView):
    template_name = 'home/article_detail.html'

    def get_context_data(self, **kwargs):
        from django.shortcuts import get_object_or_404
        from .models import Article
        data = super().get_context_data(**kwargs)
        data['article'] = get_object_or_404(Article, slug=self.kwargs['slug'], is_published=True)
        return data


class ExperienceListView(TemplateView):
    template_name = 'home/experience_list.html'

    def get_context_data(self, **kwargs):
        from .portfolio_data import get_portfolio_data
        data = super().get_context_data(**kwargs)
        data.update(get_portfolio_data())
        data['work_experiences'] = data['cv_profile']['experience']
        return data


class ExperienceDetailView(ExperienceListView):
    template_name = 'home/experience_detail.html'

    def get_context_data(self, **kwargs):
        from django.http import Http404
        data = super().get_context_data(**kwargs)
        data['experience'] = next((item for item in data['work_experiences'] if item['slug'] == self.kwargs['slug']), None)
        if not data['experience']:
            raise Http404('Experience not found')
        return data
