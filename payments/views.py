# views.py
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .actions import bulk_insert, initiate_esewa, verify_esewa_payment
from .filters import PaymentFilter
from .models import Payment
from .serializers import PaymentSerializer


@generate_bulk_schema_view("Payment", PaymentSerializer)
@generate_crud_schema_view("Payment")
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="all",
                type=str,
                description="If set to `true`, disables pagination and returns all payments.",
                required=False,
                enum=["true", "false"],
            ),
            OpenApiParameter(
                name="method",
                type=str,
                description="Filter payments by payment method.",
                required=False,
            ),
            OpenApiParameter(
                name="payment_status",
                type=str,
                description="Filter payments by payment status.",
                required=False,
            ),
            OpenApiParameter(
                name="paid_at_before",
                type=str,
                description="Filter payments made before this datetime (YYYY-MM-DDTHH:MM:SS).",
                required=False,
            ),
            OpenApiParameter(
                name="paid_at_after",
                type=str,
                description="Filter payments made after this datetime (YYYY-MM-DDTHH:MM:SS).",
                required=False,
            ),
        ],
        tags=["Payment"],
        summary="Retrieve a list of payments",
        description="Fetch all payments available in the system.",
    )
)
class PaymentViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    search_fields = [
        "order__id",
        "transaction_id",
        "method",
        "payment_status",
        "card_last4",
        "card_brand",
    ]
    ordering_fields = ["amount", "paid_at", "created_at"]
    ordering = ["-created_at"]
    bulk_schema_tag = "Payment"

    permission_classes_by_action = {
        "default": [IsAuthenticated],
    }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        currency = self.request.query_params.get("currency", "NPR").upper()
        context["currency"] = currency
        return context

    # Custom action assignments
    bulk_insert = bulk_insert
    verify_esewa_payment = verify_esewa_payment
    initiate_esewa = initiate_esewa
