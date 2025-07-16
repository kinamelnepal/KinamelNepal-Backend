from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .actions import bulk_insert
from .filters import ProductFilter
from .models import Product
from .serializers import ProductSerializer


@generate_bulk_schema_view("Product", ProductSerializer)
@generate_crud_schema_view("Product")
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="all",
                type=str,
                description="If set to `true`, disables pagination and returns all orders.",
                required=False,
                enum=["true", "false"],
            ),
            OpenApiParameter(
                name="currency",
                type=str,
                description="Convert price fields to this currency (USD, EUR, NPR). Default is USD.",
                required=False,
                enum=["NPR", "USD", "EUR"],
            ),
        ],
        tags=["Order"],
        summary="Retrieve a list of orders",
        description="Fetch all orders available in the system.",
    )
)
class ProductViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ["title", "brand"]
    ordering_fields = [
        "id",
        "new_price",
        "old_price",
        "rating",
        "sku",
        "created_at",
        "updated_at",
        "quantity",
        "weight",
        "title",
    ]
    ordering = ["-created_at"]
    bulk_schema_tag = "Product"

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "bulk_insert": [IsAuthenticated, IsAdminUser],
        "create": [IsAuthenticated, IsAdminUser],
        "update": [IsAuthenticated, IsAdminUser],
        "partial_update": [IsAuthenticated, IsAdminUser],
        "destroy": [IsAuthenticated, IsAdminUser],
        "default": [AllowAny],
    }

    def paginate_queryset(self, queryset):
        all_param = self.request.query_params.get("all", None)
        if all_param == "true":
            return None
        return super().paginate_queryset(queryset)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        currency = self.request.query_params.get("currency", "NPR").upper()
        context["currency"] = currency
        return context

    # ✅ Assign custom action
    bulk_insert = bulk_insert
