"""Accept historical home.* permission checks during the domain transition."""

from django.contrib.auth.backends import ModelBackend

from .compatibility import LEGACY_MODEL_APPS


class LegacyPermissionBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if perm.startswith("home."):
            codename = perm.split(".", 1)[1]
            domain = LEGACY_MODEL_APPS.get(codename.rsplit("_", 1)[-1])
            if domain:
                perm = f"{domain}.{codename}"
        return super().has_perm(user_obj, perm, obj)

    def has_module_perms(self, user_obj, app_label):
        if app_label == "home":
            return any(
                super(LegacyPermissionBackend, self).has_module_perms(user_obj, domain)
                for domain in set(LEGACY_MODEL_APPS.values())
            )
        return super().has_module_perms(user_obj, app_label)
