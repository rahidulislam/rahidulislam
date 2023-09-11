from typing import Any
from django.views.generic import TemplateView
from .models import SocialMedia,PersonalInfo
# Create your views here.

class HomeView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data =  super().get_context_data(**kwargs)
        data['social_items'] = SocialMedia.objects.all()
        data['personal_info'] = PersonalInfo.objects.first()
        return data

