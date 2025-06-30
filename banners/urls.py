from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BannerViewSet

router = DefaultRouter()
router.register(r"", BannerViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
