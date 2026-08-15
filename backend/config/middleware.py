from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class LocalFrontendCorsMiddleware:
    """Allow credentials only from explicitly configured local frontend origins."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")

        if request.method == "OPTIONS" and origin in settings.FRONTEND_ALLOWED_ORIGINS:
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if origin and origin in settings.FRONTEND_ALLOWED_ORIGINS:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            patch_vary_headers(response, ["Origin"])

        return response
