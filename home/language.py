from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def language_context(request):
    return {'portfolio_language': 'bn' if request.COOKIES.get('portfolio_language') == 'bn' else 'en'}


@require_POST
def set_language(request):
    language = request.POST.get('language', 'en')
    if language not in ('bn', 'en'):
        language = 'en'
    target = request.POST.get('next', '/')
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        target = '/'
    response = HttpResponseRedirect(target)
    response.set_cookie('portfolio_language', language, max_age=31536000, samesite='Lax', secure=request.is_secure())
    return response
