from django import forms
from django.core.cache import cache
from django.core.exceptions import ValidationError
from .models import Contact


class ContactForm(forms.ModelForm):
    # Deliberately not part of Contact: this field catches unsophisticated bots
    # without exposing an extra column or changing the persisted data model.
    website = forms.CharField(required=False, label="", widget=forms.TextInput(
        attrs={"class": "contact-trap", "autocomplete": "off", "tabindex": "-1", "style": "display:none"}))

    def __init__(self, *args, **kwargs):
        self.request_ip = kwargs.pop("request_ip", "unknown")
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Your Name"})
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Your Email"})
        self.fields["subject"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Subject"})
        self.fields["message"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Message", "rows": "5"})

    def clean(self):
        cleaned = super().clean()
        ip = self.request_ip
        if cleaned.get("website") or not self._within_rate_limit(ip):
            raise ValidationError("We couldn't accept that message. Please try again later.")
        return cleaned

    @staticmethod
    def _within_rate_limit(ip):
        key = f"contact-submit:{ip}"
        try:
            count = cache.get(key)
            if count is None:
                cache.add(key, 1, 300)
                return True
            if int(count) >= 3:
                return False
            cache.incr(key)
            return True
        except (ValueError, TypeError):
            return True

    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'message')
