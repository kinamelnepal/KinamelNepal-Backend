from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from core.mixins import MultiLookupMixin

from .filters import PrivacyPolicyFilter
from .models import PrivacyPolicy
from .serializers import PrivacyPolicySerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Privacy Policy"],
        summary="Retrieve a list of Privacy Policy",
        description="Fetch all privacy Policy.",
        parameters=[
            OpenApiParameter(
                name="all",
                type=str,
                description="If set to `true`, disables pagination and returns all Privacy Policy.",
                required=False,
                enum=["true", "false"],
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Privacy Policy"],
        summary="Retrieve a specific Privacy Policy",
        description="Fetch detailed information about a specific Privacy Policy by its ID.",
    ),
    create=extend_schema(
        tags=["Privacy Policy"],
        summary="Create a new Privacy Policy",
        description="Add a new Privacy Policy record.",
    ),
    update=extend_schema(
        tags=["Privacy Policy"],
        summary="Update an Privacy Policy",
        description="Modify an existing Privacy Policy completely.",
    ),
    partial_update=extend_schema(
        tags=["Privacy Policy"],
        summary="Partially update an Privacy Policy",
        description="Modify part of an existing Privacy Policy.",
    ),
    destroy=extend_schema(
        tags=["Privacy Policy"],
        summary="Delete an Privacy Policy",
        description="Remove an Privacy Policy by its ID.",
    ),
)
class PrivacyPolicyViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = PrivacyPolicy.objects.all()
    serializer_class = PrivacyPolicySerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def paginate_queryset(self, queryset):
        all_param = self.request.query_params.get("all", None)
        if all_param == "true":
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PrivacyPolicyFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
