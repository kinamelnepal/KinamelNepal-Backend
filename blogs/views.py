from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import BlogFilter
from .models import Blog, BlogCategory
from .serializers import BlogCategorySerializer, BlogSerializer


@generate_bulk_schema_view("Blog", BlogSerializer)
@generate_crud_schema_view("Blog")
class BlogViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    filterset_class = BlogFilter
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    bulk_schema_tag = "Blog"

    search_fields = ["title", "category__name"]
    ordering_fields = ["id", "date", "created_at", "updated_at"]
    ordering = ["-created_at"]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    permission_classes_by_action = {
        "bulk_insert": [IsAuthenticated, IsAdminUser],
        "create": [IsAuthenticated, IsAdminUser],
        "update": [IsAuthenticated, IsAdminUser],
        "partial_update": [IsAuthenticated, IsAdminUser],
        "destroy": [IsAuthenticated, IsAdminUser],
        "retrieve": [AllowAny],
        "list": [AllowAny],
        "default": [AllowAny],
    }


@generate_bulk_schema_view("Blog", BlogSerializer)
@generate_crud_schema_view("BlogCategory")
class BlogCategoryViewSet(MultiLookupMixin, BaseViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    search_fields = ["name"]
    ordering_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    permission_classes_by_action = {
        "create": [IsAuthenticated, IsAdminUser],
        "update": [IsAuthenticated, IsAdminUser],
        "partial_update": [IsAuthenticated, IsAdminUser],
        "destroy": [IsAuthenticated, IsAdminUser],
        "retrieve": [AllowAny],
        "list": [AllowAny],
        "default": [AllowAny],
    }
