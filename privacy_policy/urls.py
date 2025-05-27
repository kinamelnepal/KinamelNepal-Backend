from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrivacyPolicyViewSet

router = DefaultRouter()
router.register(r'', PrivacyPolicyViewSet, basename='privacy-policy')

urlpatterns = [
    path('', include(router.urls)),
]
