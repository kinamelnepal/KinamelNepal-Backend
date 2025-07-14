# hosapp/authentication.py
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    keyword = "X-API-KEY"

    def authenticate(self, request):
        api_key = request.headers.get(self.keyword)
        if not api_key:
            return None

        try:
            APIKey.objects.get(key=api_key, is_active=True)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive API key.")
        return (AnonymousUser(), api_key)
