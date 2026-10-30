from datetime import timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone


class OwnerAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            raise ValidationError(
                "This dashboard is available to the site owner only.", code="owner_only"
            )


class AnalyticsFilterForm(forms.Form):
    period = forms.ChoiceField(
        choices=[
            ("7", "Last 7 days"),
            ("30", "Last 30 days"),
            ("90", "Last 90 days"),
            ("custom", "Custom dates"),
        ],
        required=False,
    )
    start = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    end = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )

    def clean(self):
        data = super().clean()
        today = timezone.localdate()
        if data.get("period") == "custom":
            start, end = data.get("start"), data.get("end")
            if not start or not end:
                raise ValidationError("Choose both dates for a custom range.")
            if start > end or end > today or (end - start).days > 365:
                raise ValidationError(
                    "Choose an ordered range of up to 366 days ending today or earlier."
                )
        else:
            end = today
            start = today - timedelta(days=int(data.get("period") or "30") - 1)
        data.update(start=start, end=end)
        return data


class EnquiryActionForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ("read", "Mark read"),
            ("replied", "Mark replied"),
            ("retry", "Retry notification"),
        ]
    )
