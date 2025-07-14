from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TermsAndConditionsViewSet

router = DefaultRouter()
router.register(r"", TermsAndConditionsViewSet, basename="terms-and-conditions")

urlpatterns = [
    path("", include(router.urls)),
]
