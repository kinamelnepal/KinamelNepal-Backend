from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'order', OrderViewSet, basename='order')
router.register(r'order-item', OrderItemViewSet, basename='order-item')

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
]
