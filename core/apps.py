from django.contrib.admin.apps import AdminConfig


class PortfolioAdminConfig(AdminConfig):
    default_site = "core.admin.PortfolioAdminSite"
