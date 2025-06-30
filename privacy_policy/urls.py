from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrivacyPolicyViewSet

router = DefaultRouter()
router.register(r"", PrivacyPolicyViewSet, basename="privacy-policy")

urlpatterns = [
    path("", include(router.urls)),
]
