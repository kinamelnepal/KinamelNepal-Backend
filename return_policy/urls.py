from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReturnPolicyViewSet

router = DefaultRouter()
router.register(r'', ReturnPolicyViewSet, basename='return-policy')

urlpatterns = [
    path('', include(router.urls)),
]
