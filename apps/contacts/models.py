from django.core.validators import RegexValidator
from django.db import models


class PublicContact(models.Model):
    email = models.EmailField(blank=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                r"^\+?[0-9]{7,15}$", "Use an international number, e.g. +8801612061077."
            )
        ],
    )
    whatsapp = models.CharField(
        "WhatsApp number",
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                r"^\+?[0-9]{7,15}$", "Use an international number, e.g. +8801612061077."
            )
        ],
    )
    telegram = models.CharField(
        "Telegram username",
        max_length=32,
        blank=True,
        validators=[
            RegexValidator(
                r"^[A-Za-z][A-Za-z0-9_]{4,31}$",
                "Enter your username without @ or a URL.",
            )
        ],
    )
    location = models.CharField(
        max_length=100, blank=True, help_text="Public city/country; optional."
    )
    github = models.URLField("GitHub URL", blank=True)
    linkedin = models.URLField("LinkedIn URL", blank=True)

    class Meta:
        db_table = "home_publiccontact"
        verbose_name = "Public contact details"
        verbose_name_plural = "Public contact details"

    def __str__(self):
        return "Public contact details"

    @property
    def whatsapp_url(self):
        return f'https://wa.me/{self.whatsapp.lstrip("+")}' if self.whatsapp else ""

    @property
    def telegram_url(self):
        return f"https://t.me/{self.telegram}" if self.telegram else ""


class Contact(models.Model):
    STATUS_CHOICES = [("unread", "Unread"), ("read", "Read"), ("replied", "Replied")]
    DELIVERY_CHOICES = [("pending", "Pending"), ("sent", "Sent"), ("failed", "Failed")]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="unread")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    notification_status = models.CharField(
        max_length=12, choices=DELIVERY_CHOICES, default="pending"
    )

    class Meta:
        db_table = "home_contact"
        ordering = ["-created_at", "-pk"]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.email
