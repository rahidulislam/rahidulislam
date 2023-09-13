from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Your Name"})
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Your Email"})
        self.fields["subject"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Subject"})
        self.fields["message"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Message", "rows": "5"})

    class Meta:
        model = Contact
        fields = '__all__'
