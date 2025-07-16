from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import OrderFilter, OrderItemFilter
from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer


@generate_bulk_schema_view("Order", OrderSerializer)
@generate_crud_schema_view("Order")
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
class OrderViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = OrderFilter
    search_fields = ["full_name", "email", "phone_number"]
    ordering_fields = ["total", "order_status", "created_at"]
    ordering = ["-created_at"]

    permission_classes_by_action = {
        "bulk_insert": [IsAuthenticated],
        "create": [IsAuthenticated],
        "list": [IsAuthenticated],
        "retrieve": [IsAuthenticated],
        "update": [IsAuthenticated],
        "partial_update": [IsAuthenticated],
        "destroy": [IsAuthenticated],
        "default": [IsAuthenticated],
    }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        currency = self.request.query_params.get("currency", "NPR").upper()
        context["currency"] = currency
        return context

    @extend_schema(
        tags=["Order"],
        summary="Bulk Insert Orders",
        description="Insert multiple orders into the system in a single request.",
        request=OrderSerializer(many=True),
    )
    @action(detail=False, methods=["post"])
    def bulk_insert(self, request, *args, **kwargs):
        orders_data = request.data
        if not isinstance(orders_data, list) or len(orders_data) == 0:
            return Response(
                {"detail": "Expected 'orders' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=orders_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": f"{len(orders_data)} orders successfully inserted."},
            status=status.HTTP_201_CREATED,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


@generate_bulk_schema_view("Order Item", OrderItemSerializer)
@generate_crud_schema_view("Order Item")
class OrderItemViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderItemFilter
    ordering_fields = ["total", "quantity", "price"]
    ordering = ["-total"]

    permission_classes_by_action = {
        "bulk_insert": [IsAuthenticated],
        "create": [IsAuthenticated],
        "list": [IsAuthenticated],
        "retrieve": [IsAuthenticated],
        "update": [IsAuthenticated],
        "partial_update": [IsAuthenticated],
        "destroy": [IsAuthenticated],
        "default": [IsAuthenticated],
    }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        currency = self.request.query_params.get("currency", "NPR").upper()
        context["currency"] = currency
        return context

    @extend_schema(
        tags=["Order Item"],
        summary="Bulk Insert Order items",
        description="Insert multiple orders items into the system in a single request.",
        request=OrderItemSerializer(many=True),
    )
    @action(detail=False, methods=["post"])
    def bulk_insert(self, request, *args, **kwargs):
        order_items_data = request.data
        if not isinstance(order_items_data, list) or len(order_items_data) == 0:
            return Response(
                {"detail": "Expected 'order_items' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=order_items_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": f"{len(order_items_data)} order items successfully inserted."},
            status=status.HTTP_201_CREATED,
        )
