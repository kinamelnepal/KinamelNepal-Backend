from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from core.mixins import MultiLookupMixin

from .filters import FaqFilter
from .models import Faq
from .serializers import FaqSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["FAQs"],
        summary="Retrieve a list of FAQs",
        description="Fetch all frequently asked questions.",
        parameters=[
            OpenApiParameter(
                name="all",
                type=str,
                description="If set to `true`, disables pagination and returns all FAQs.",
                required=False,
                enum=["true", "false"],
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["FAQs"],
        summary="Retrieve a specific FAQ",
        description="Fetch detailed information about a specific FAQ by its ID.",
    ),
    create=extend_schema(
        tags=["FAQs"],
        summary="Create a new FAQ",
        description="Add a new frequently asked question.",
    ),
    update=extend_schema(
        tags=["FAQs"],
        summary="Update an FAQ",
        description="Modify an existing FAQ completely.",
    ),
    partial_update=extend_schema(
        tags=["FAQs"],
        summary="Partially update an FAQ",
        description="Modify part of an existing FAQ.",
    ),
    destroy=extend_schema(
        tags=["FAQs"],
        summary="Delete an FAQ",
        description="Remove an FAQ by its ID.",
    ),
)
class FaqViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer
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
    filterset_class = FaqFilter
    search_fields = ["question"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
