from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderItemViewSet, OrderViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r"order", OrderViewSet, basename="order")
router.register(r"order-item", OrderItemViewSet, basename="order-item")

urlpatterns = [
    path("", include(router.urls)),
]
