from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
]
