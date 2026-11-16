from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.template import loader


def error_404(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def error_500(request: HttpRequest) -> HttpResponse:
    # Render without the request so no context processor touches the database.
    return HttpResponseServerError(loader.get_template("500.html").render())
