from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet

# Initialize the DefaultRouter
router = DefaultRouter()

# Register the AddressViewSet with the router
router.register(r'address', AddressViewSet, basename='address')

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls)),  
]
