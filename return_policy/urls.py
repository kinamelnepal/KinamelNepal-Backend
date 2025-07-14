from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReturnPolicyViewSet

router = DefaultRouter()
router.register(r"", ReturnPolicyViewSet, basename="return-policy")

urlpatterns = [
    path("", include(router.urls)),
]
