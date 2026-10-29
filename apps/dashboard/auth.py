from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import never_cache


def owner_required(view):
    @wraps(view)
    @never_cache
    def guarded(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(), login_url="dashboard:login"
            )
        if not (request.user.is_active and request.user.is_superuser):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return guarded
