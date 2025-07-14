from django.http import JsonResponse

from .models import APIKey
from .utils import set_current_user


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(request.user)
        response = self.get_response(request)
        return response


class APIKeyMiddleware:
    """
    Middleware to check for a valid API key in the request headers,
    but whitelist certain URLs like admin and docs.
    """

    # Add your whitelisted URL prefixes here
    WHITELIST_PATHS = [
        "/admin/",
        "/api/schema/",
        "/api/schema/swagger-ui/",
        "/api/schema/redoc/",
        "/api/docs/",
        "/ckeditor/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        print("path", path)

        # Skip API key check for whitelisted URLs
        if any(path.startswith(p) for p in self.WHITELIST_PATHS):
            return self.get_response(request)

        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return JsonResponse({"detail": "API key header missing."}, status=401)

        try:
            key_obj = APIKey.objects.get(key=api_key, is_active=True)
        except APIKey.DoesNotExist:
            return JsonResponse({"detail": "Invalid or inactive API key."}, status=403)

        request.api_key = key_obj
        return self.get_response(request)
