from django.http import Http404
from django.views.generic import TemplateView

from .presentation import profile_context


class ExperienceListView(TemplateView):
    template_name = "home/experience_list.html"

    def get_context_data(self, **kwargs):
        data = {**super().get_context_data(**kwargs), **profile_context()}
        data["work_experiences"] = data["cv_profile"]["experience"]
        return data


class ExperienceDetailView(ExperienceListView):
    template_name = "home/experience_detail.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["experience"] = next(
            (
                item
                for item in data["work_experiences"]
                if item["slug"] == self.kwargs["slug"]
            ),
            None,
        )
        if not data["experience"]:
            raise Http404("Experience not found")
        return data
