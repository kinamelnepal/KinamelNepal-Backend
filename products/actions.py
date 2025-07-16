from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import ProductSerializer


@extend_schema(
    tags=["Product"],
    summary="Bulk Insert Products",
    description="Insert multiple products into the system in a single request.",
    request=ProductSerializer(many=True),
)
@action(detail=False, methods=["post"])
def bulk_insert(self, request, *args, **kwargs):
    """
    Bulk insert products into the system.
    Accepts a list of products to insert.
    """
    products_data = request.data

    if not isinstance(products_data, list) or len(products_data) == 0:
        return Response(
            {"detail": "Expected 'products' to be a non-empty list."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ProductSerializer(
        data=products_data, many=True, context=self.get_serializer_context()
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"detail": f"{len(products_data)} products successfully inserted."},
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
