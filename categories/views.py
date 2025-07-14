from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import CategoryFilter
from .models import Category
from .serializers import CategorySerializer


@generate_bulk_schema_view("Category", CategorySerializer)
@generate_crud_schema_view("Category")
class CategoryViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    search_fields = ["name"]
    ordering_fields = ["id", "name", "item", "num", "created_at", "updated_at"]
    ordering = ["-created_at"]
    bulk_schema_tag = "Category"

    permission_classes_by_action = {
        "create": [IsAuthenticated, IsAdminUser],
        "update": [IsAuthenticated, IsAdminUser],
        "partial_update": [IsAuthenticated, IsAdminUser],
        "destroy": [IsAuthenticated, IsAdminUser],
        "bulk_create": [IsAuthenticated, IsAdminUser],
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "default": [AllowAny],
    }
