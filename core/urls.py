from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import APIKeyViewSet, HealthCheckView

router = DefaultRouter()
router.register(r"keys", APIKeyViewSet, basename="api-key")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("api/health-check/", HealthCheckView.as_view(), name="health-check"),
    path("api/user/", include("users.urls"), name="user-apis"),
    path("api/category/", include("categories.urls"), name="category-apis"),
    path("api/product/", include("products.urls"), name="product-apis"),
    path("api/contact/", include("contacts.urls"), name="contact-apis"),
    path("api/faq/", include("faqs.urls"), name="faq-apis"),
    path("api/banner/", include("banners.urls"), name="banner-apis"),
    path("api/", include("blogs.urls"), name="blog-apis"),
    path("api/", include("carts.urls"), name="cart-apis"),
    path("api/account/", include("accounts.urls"), name="account-apis"),
    path("api/payment/", include("payments.urls"), name="payment-apis"),
    path(
        "api/terms-and-conditions/",
        include("terms_and_conditions.urls"),
        name="terms-and-conditions-apis",
    ),
    path("api/", include("orders.urls"), name="order-apis"),
    path(
        "api/privacy-policy/",
        include("privacy_policy.urls"),
        name="privacy-policy-apis",
    ),
    path(
        "api/return-policy/", include("return_policy.urls"), name="return-policy-apis"
    ),
    path("api/", include(router.urls), name="core"),
]


# Serve media files when DEBUG=False (production)
if not settings.DEBUG:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
