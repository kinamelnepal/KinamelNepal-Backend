import requests
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.mixins import MultiLookupMixin

from .filters import PaymentFilter
from .models import Payment
from .serializers import EsewaVerificationSerializer, PaymentSerializer
from .utils import initiate_esewa_payment


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
    ),
    retrieve=extend_schema(
        tags=["Payment"],
        summary="Retrieve a specific payment",
        description="Fetch detailed information about a specific payment by its ID.",
    ),
    create=extend_schema(
        tags=["Payment"],
        summary="Create a new payment",
        description="Create a new payment with the required details.",
    ),
    update=extend_schema(
        tags=["Payment"],
        summary="Update a payment's details",
        description="Modify an existing payment's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Payment"],
        summary="Partially update a payment's details",
        description="Modify some fields of an existing payment (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Payment"],
        summary="Delete a payment",
        description="Remove a payment from the system by its ID.",
    ),
)
class PaymentViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
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

    def get_permissions(self):
        return [IsAuthenticated()]

    def paginate_queryset(self, queryset):
        """
        Override paginate_queryset to check for 'all=true' query parameter.
        """
        all_param = self.request.query_params.get("all", None)
        if all_param == "true":
            return None
        return super().paginate_queryset(queryset)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        currency = self.request.query_params.get("currency", "NPR").upper()
        context["currency"] = currency
        return context

    @extend_schema(
        tags=["Payment"],
        summary="Bulk Insert Payments",
        description="Insert multiple payments into the system in a single request.",
        request=PaymentSerializer(many=True),
    )
    @action(detail=False, methods=["post"])
    def bulk_insert(self, request, *args, **kwargs):
        """
        Bulk insert payments into the system.
        Accepts a list of payments to insert.
        """
        payments_data = request.data

        if not isinstance(payments_data, list) or len(payments_data) == 0:
            return Response(
                {"detail": "Expected a non-empty list of payments."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PaymentSerializer(data=payments_data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"{len(payments_data)} payments successfully inserted."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Payment"],
        summary="Verify eSewa Payment",
        description="Verify a payment made via eSewa using `oid`, `amt`, and `refId`.",
        request=EsewaVerificationSerializer,
        responses={200: PaymentSerializer},
    )
    @action(detail=False, methods=["post"], url_path="verify-esewa")
    def verify_esewa_payment(self, request):
        """
        Verify eSewa payment using the refId returned by eSewa after a successful transaction.
        """
        serializer = EsewaVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        oid = data["oid"]  # Order ID
        amt = data["amt"]  # Amount
        ref_id = data["refId"]  # Reference ID from eSewa

        # eSewa Verification Endpoint
        verify_url = "https://uat.esewa.com.np/epay/transrec"
        payload = {"amt": amt, "rid": ref_id, "pid": oid, "scd": "EPAYTEST"}

        try:
            response = requests.post(verify_url, data=payload)
            if "<response_code>Success</response_code>" in response.text:
                payment = get_object_or_404(Payment, transaction_id=oid)
                payment.payment_status = "COMPLETED"
                payment.save()
                return Response(
                    PaymentSerializer(payment).data, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Verification failed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Payment"],
        summary="Generate eSewa Payment URL",
        description="Generate a URL to redirect users to eSewa for payment.",
    )
    @action(detail=True, methods=["post"], url_path="initiate-esewa")
    def initiate_esewa(self, request, pk=None):
        payment = self.get_object()
        response_data = initiate_esewa_payment(payment)
        return Response(response_data)
