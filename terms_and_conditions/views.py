from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from core.mixins import MultiLookupMixin
from .filters import TermsAndConditionsFilter
from .serializers import TermsAndConditionsSerializer
from .models import TermsAndConditions

@extend_schema_view(
    list=extend_schema(
        tags=["Terms and Conditions"],
        summary="Retrieve a list of Terms and Conditions",
        description="Fetch all terms and conditions.",
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all Terms and Conditions.',
                required=False,
                enum=['true', 'false']
            )
        ]
    ),
    retrieve=extend_schema(
        tags=["Terms and Conditions"],
        summary="Retrieve a specific Terms and Conditions",
        description="Fetch detailed information about a specific Terms and Conditions by its ID.",
    ),
    create=extend_schema(
        tags=["Terms and Conditions"],
        summary="Create a new Terms and Conditions",
        description="Add a new Terms and Conditions record.",
    ),
    update=extend_schema(
        tags=["Terms and Conditions"],
        summary="Update an Terms and Conditions",
        description="Modify an existing Terms and Conditions completely.",
    ),
    partial_update=extend_schema(
        tags=["Terms and Conditions"],
        summary="Partially update an Terms and Conditions",
        description="Modify part of an existing Terms and Conditions.",
    ),
    destroy=extend_schema(
        tags=["Terms and Conditions"],
        summary="Delete an Terms and Conditions",
        description="Remove an Terms and Conditions by its ID.",
    ),
)
class TermsAndConditionsViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = TermsAndConditions.objects.all()
    serializer_class = TermsAndConditionsSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def paginate_queryset(self, queryset):
        all_param = self.request.query_params.get('all', None)
        if all_param == 'true':
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TermsAndConditionsFilter
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
