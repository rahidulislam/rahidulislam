"""Preserve bookmarked admin routes and names while domains gain ownership."""

from django.apps import apps
from django.contrib.admin import AdminSite
from django.urls import path

from .compatibility import LEGACY_MODEL_APPS


class PortfolioAdminSite(AdminSite):
    def get_urls(self):
        aliases = []
        for model_name, app in LEGACY_MODEL_APPS.items():
            model = apps.get_model(app, model_name)
            if not self.is_registered(model):
                continue
            model_admin = self.get_model_admin(model)
            for pattern in model_admin.get_urls():
                name = pattern.name
                if name and name.startswith(f"{app}_"):
                    name = "home_" + name[len(app) + 1 :]
                aliases.append(
                    path(
                        f"home/{model._meta.model_name}/{pattern.pattern}",
                        pattern.callback,
                        name=name,
                    )
                )
        return aliases + super().get_urls()
