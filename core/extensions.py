from drf_spectacular.extensions import OpenApiAuthenticationExtension


class APIKeyAuthScheme(OpenApiAuthenticationExtension):
    target_class = "core.authentication.APIKeyAuthentication"  # Update this to your actual import path
    name = (
        "ApiKeyAuth"  # This name must match the one in SPECTACULAR_SETTINGS > SECURITY
    )

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-KEY",
        }
