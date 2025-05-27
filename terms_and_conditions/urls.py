from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TermsAndConditionsViewSet

router = DefaultRouter()
router.register(r'', TermsAndConditionsViewSet, basename='terms-and-conditions')

urlpatterns = [
    path('', include(router.urls)),
]
