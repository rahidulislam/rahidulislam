from django import forms
from django.core.exceptions import ValidationError

from .models import Contact
from .services import consume_submission_slot


class ContactForm(forms.ModelForm):
    # Deliberately not part of Contact: this field catches unsophisticated bots
    # without exposing an extra column or changing the persisted data model.
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "contact-trap",
                "autocomplete": "off",
                "tabindex": "-1",
                "style": "display:none",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.request_language = kwargs.pop("request_language", "en")
        self.request_ip = kwargs.pop("request_ip", "unknown")
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Your Name"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Your Email"}
        )
        self.fields["subject"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Subject"}
        )
        self.fields["message"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Message", "rows": "5"}
        )

        if self.request_language == "bn":
            placeholders = {
                "name": "আপনার নাম",
                "email": "আপনার ইমেইল",
                "subject": "বিষয়",
                "message": "আপনার বার্তা",
            }
            for name, placeholder in placeholders.items():
                self.fields[name].widget.attrs["placeholder"] = placeholder
                self.fields[name].error_messages["required"] = "এই তথ্যটি পূরণ করুন।"
                self.fields[name].error_messages[
                    "max_length"
                ] = "সর্বোচ্চ %(limit_value)d অক্ষর লিখুন।"
            self.fields["email"].error_messages["invalid"] = "সঠিক ইমেইল ঠিকানা দিন।"

    def clean(self):
        cleaned = super().clean()
        # Only complete submissions use the visitor's budget; typos do not.
        if cleaned.get("website") or (
            not self.errors and not consume_submission_slot(client_ip=self.request_ip)
        ):
            raise ValidationError(
                "এই বার্তাটি গ্রহণ করা যায়নি। পরে আবার চেষ্টা করুন।"
                if self.request_language == "bn"
                else "We couldn't accept that message. Please try again later."
            )
        return cleaned

    class Meta:
        model = Contact
        fields = ("name", "email", "subject", "message")
