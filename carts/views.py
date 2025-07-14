from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters
from rest_framework.permissions import AllowAny

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .actions import bulk_insert_cart, bulk_insert_cart_item
from .filters import CartFilter, CartItemFilter
from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


@generate_bulk_schema_view("Cart", CartSerializer)
@generate_crud_schema_view("Cart")
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
class CartViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    filterset_class = CartFilter
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    bulk_schema_tag = "Cart"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    permission_classes_by_action = {
        "create": [AllowAny],
        "retrieve": [AllowAny],
        "list": [AllowAny],
        "update": [AllowAny],
        "partial_update": [AllowAny],
        "destroy": [AllowAny],
        "bulk_insert": [AllowAny],
        "default": [AllowAny],
    }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["currency"] = self.request.query_params.get("currency", "NPR").upper()
        return context

    bulk_insert_cart = bulk_insert_cart


@generate_bulk_schema_view("Cart Item", CartItemSerializer)
@generate_crud_schema_view("Cart Item")
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
class CartItemViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    filterset_class = CartItemFilter
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    bulk_schema_tag = "Cart Item"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "product__title",
        "cart__user__first_name",
        "cart__user__last_name",
    ]
    ordering_fields = ["created_at", "updated_at", "product__title", "quantity"]
    ordering = ["product__title"]

    permission_classes_by_action = {
        "create": [AllowAny],
        "retrieve": [AllowAny],
        "list": [AllowAny],
        "update": [AllowAny],
        "partial_update": [AllowAny],
        "destroy": [AllowAny],
        "bulk_insert_cart_item": [AllowAny],
        "default": [AllowAny],
    }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["currency"] = self.request.query_params.get("currency", "NPR").upper()
        return context

    bulk_insert_cart_item = bulk_insert_cart_item
