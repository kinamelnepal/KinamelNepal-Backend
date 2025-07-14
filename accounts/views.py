from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from core.mixins import MultiLookupMixin

from .filters import AddressFilter
from .models import Address
from .serializers import AddressSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Address"],
        summary="Retrieve a list of addresses",
        description="Fetch all addresses stored in the system.",
        parameters=[
            OpenApiParameter(
                name="all",
                type=str,
                description="If set to `true`, disables pagination and returns all addresses.",
                required=False,
                enum=["true", "false"],
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Address"],
        summary="Retrieve a specific address",
        description="Fetch detailed information about a specific address by its ID.",
    ),
    create=extend_schema(
        tags=["Address"],
        summary="Create a new address",
        description="Add a new address for a user.",
    ),
    update=extend_schema(
        tags=["Address"],
        summary="Update an address",
        description="Fully update an existing address.",
    ),
    partial_update=extend_schema(
        tags=["Address"],
        summary="Partially update an address",
        description="Update select fields of an existing address.",
    ),
    destroy=extend_schema(
        tags=["Address"],
        summary="Delete an address",
        description="Remove an address by its ID.",
    ),
)
class AddressViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AddressFilter
    ordering_fields = ["id", "full_name", "created_at"]
    ordering = ["-created_at"]

    def get_permissions(self):
        return [IsAuthenticated()]

    def paginate_queryset(self, queryset):
        all_param = self.request.query_params.get("all", None)
        if all_param == "true":
            return None
        return super().paginate_queryset(queryset)
