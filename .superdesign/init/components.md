Django templates; Bootstrap 5 utilities, no standalone UI primitive library.
## templates/base/messages.html
```
{% if messages %}
    {% for message in messages %}
      <div class="alert {% if message.tags %}alert-{{message.tags}}{% endif %} alert-dismissible fade show" role="alert">
        <strong>{{message}}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    {% endfor %}
  {% endif %}
```

## home/forms.py
```
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

```