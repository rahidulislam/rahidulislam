from django.http import HttpRequest, HttpResponse


def download_cv(request: HttpRequest) -> HttpResponse:
    """Generate from the same live content used by the portfolio."""
    from io import BytesIO

    from django.http import FileResponse, HttpResponseNotAllowed

    from .services import generate_cv

    if request.method not in ("GET", "HEAD"):
        return HttpResponseNotAllowed(["GET", "HEAD"])
    response = FileResponse(
        BytesIO(generate_cv()),
        as_attachment=True,
        filename="Rahidul_Islam_Python_Developer_CV.pdf",
        content_type="application/pdf",
    )
    response["Cache-Control"] = "no-store"
    return response
