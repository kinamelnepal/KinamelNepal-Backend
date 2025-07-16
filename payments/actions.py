import requests
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payment
from .serializers import EsewaVerificationSerializer, PaymentSerializer
from .utils import initiate_esewa_payment


@extend_schema(
    tags=["Payment"],
    summary="Bulk Insert Payments",
    description="Insert multiple payments into the system in a single request.",
    request=PaymentSerializer(many=True),
)
@action(detail=False, methods=["post"])
def bulk_insert(self, request, *args, **kwargs):
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
    serializer = EsewaVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    oid, amt, ref_id = data["oid"], data["amt"], data["refId"]

    verify_url = "https://uat.esewa.com.np/epay/transrec"
    payload = {"amt": amt, "rid": ref_id, "pid": oid, "scd": "EPAYTEST"}

    try:
        response = requests.post(verify_url, data=payload)
        if "<response_code>Success</response_code>" in response.text:
            payment = get_object_or_404(Payment, transaction_id=oid)
            payment.payment_status = "COMPLETED"
            payment.save()
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Verification failed."}, status=status.HTTP_400_BAD_REQUEST
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
