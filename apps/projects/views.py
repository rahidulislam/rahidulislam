from django.http import Http404
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

from apps.profiles.presentation import identity_context

from .catalog import filter_catalog
from .presentation import case_study_context, project_context
from .selectors import project_by_pk, published_categories


class LegacyProjectDetailView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        project = project_by_pk(pk=kwargs["pk"])
        if project is None:
            raise Http404("Project not found")
        return reverse("home:case_study", args=[project.slug])


class CaseStudyView(TemplateView):
    template_name = "home/case_study.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **case_study_context(slug=self.kwargs["slug"]),
        }


class ProjectListView(TemplateView):
    template_name = "home/projects.html"

    def get_context_data(self, **kwargs):
        data = {
            **super().get_context_data(**kwargs),
            **identity_context(),
            **project_context(),
        }
        query = self.request.GET.get("q", "")[:200].strip()
        work_type = self.request.GET.get("type", "")
        technology = self.request.GET.get("technology", "")[:80]
        data["project_cards"], data["technologies"] = filter_catalog(
            data, query, work_type, technology
        )
        data.update(
            categories=published_categories(),
            project_index=True,
            query=query,
            selected_type=work_type,
            selected_technology=technology,
        )
        return data
