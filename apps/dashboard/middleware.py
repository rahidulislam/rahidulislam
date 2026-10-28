class PrivateDashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/dashboard/"):
            response["Cache-Control"] = "private, no-store, max-age=0"
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response
