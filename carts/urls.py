from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-item', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('', include(router.urls)),
]
