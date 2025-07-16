from rest_framework.permissions import IsAuthenticated

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import AddressFilter
from .models import Address
from .serializers import AddressSerializer


@generate_bulk_schema_view("Address", AddressSerializer)
@generate_crud_schema_view("Address")
class AddressViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filterset_class = AddressFilter
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    bulk_schema_tag = "Address"

    ordering_fields = ["id", "full_name", "created_at"]
    ordering = ["-created_at"]

    permission_classes_by_action = {
        "default": [IsAuthenticated],
        "list": [IsAuthenticated],
        "retrieve": [IsAuthenticated],
        "create": [IsAuthenticated],
        "update": [IsAuthenticated],
        "partial_update": [IsAuthenticated],
        "destroy": [IsAuthenticated],
        "bulk_create": [IsAuthenticated],
        "bulk_update": [IsAuthenticated],
        "bulk_delete": [IsAuthenticated],
    }
