from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import CartItemSerializer, CartSerializer


@extend_schema(
    tags=["Cart"],
    summary="Bulk Insert Cart",
    description="Insert multiple carts into the system in a single request.",
    request=CartSerializer(many=True),
)
@action(detail=False, methods=["post"], url_path="bulk_insert")
def bulk_insert_cart(self, request, *args, **kwargs):
    carts_data = request.data
    if not isinstance(carts_data, list) or not carts_data:
        return Response(
            {"detail": "Expected a non-empty list of carts."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = self.get_serializer(data=carts_data, many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(
        {"detail": f"{len(carts_data)} carts successfully inserted."},
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    tags=["Cart Item"],
    summary="Bulk Insert Cart Items",
    description="Insert multiple cart items into the system in a single request.",
    request=CartItemSerializer(many=True),
)
@action(detail=False, methods=["post"], url_path="bulk_insert")
def bulk_insert_cart_item(self, request, *args, **kwargs):
    items_data = request.data
    if not isinstance(items_data, list) or not items_data:
        return Response(
            {"detail": "Expected a non-empty list of cart items."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = self.get_serializer(data=items_data, many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(
        {"detail": f"{len(items_data)} cart items successfully inserted."},
        status=status.HTTP_201_CREATED,
    )
