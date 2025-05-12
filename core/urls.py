# from django.urls import path
# from .views import CountryListView, GeoLocationView  

# urlpatterns = [
#     path('countries/', CountryListView.as_view(), name='country-list'),  
#     path('get-lat-lng/', GeoLocationView.as_view(), name='geolocation-view'), 
# ]


from django.contrib import admin
from django.urls import path, re_path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
) 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.conf import settings
import os
from django.conf.urls.static import static
from django.views.static import serve


class HealthCheckView(APIView):
    """
    A simple health-check endpoint to verify the API's availability.
    """
    @extend_schema(
        summary="Health Check API",
        description="Returns the health status of the API.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "message": {"type": "string", "example": "The API is running smoothly."},
                },
            }
        },
    )
    def get(self, request):
        return Response(
            {"status": "healthy", "message": "The API is running smoothly."},
            status=status.HTTP_200_OK
        )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/',SpectacularAPIView.as_view(),name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs'
        ),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/health-check/',HealthCheckView.as_view(),name='health-check'),
    path('api/user/',include('users.urls'),name='user-apis'),
    path('api/category/',include('categories.urls'),name='category-apis'),
    path('api/product/',include('products.urls'),name='product-apis'),
    path('api/contact/',include('contacts.urls'),name='contact-apis'),
    path('api/faq/',include('faqs.urls'),name='faq-apis'),
    path('api/banner/',include('banners.urls'),name='banner-apis'),
    path('api/',include('blogs.urls'),name='blog-apis'),
]


# Serve media files when DEBUG=False (production)
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
