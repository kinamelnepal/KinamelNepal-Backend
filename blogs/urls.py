from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BlogCategoryViewSet, BlogViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"blog", BlogViewSet, basename="blog")
router.register(r"blog-category", BlogCategoryViewSet, basename="blog-category")

urlpatterns = [
    path("", include(router.urls)),
]
