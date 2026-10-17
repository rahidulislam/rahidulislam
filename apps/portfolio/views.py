from django.contrib import messages
from django.views.generic import FormView

from apps.contacts.forms import ContactForm
from apps.contacts.services import EnquiryInput, submit_enquiry

from .presentation import homepage_context


class HomeView(FormView):
    form_class = ContactForm
    template_name = "home/index.html"
    success_url = "/#contact"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request_language"] = self.request.COOKIES.get(
            "portfolio_language", "en"
        )
        kwargs["request_ip"] = self.request.META.get("REMOTE_ADDR", "unknown")
        return kwargs

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **homepage_context()}

    def form_valid(self, form):
        submit_enquiry(
            data=EnquiryInput(
                **{
                    key: form.cleaned_data[key]
                    for key in ("name", "email", "subject", "message")
                }
            )
        )
        messages.success(self.request, "Your message was saved. Thank you!")
        return super().form_valid(form)
