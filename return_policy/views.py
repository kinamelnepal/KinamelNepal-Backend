from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from core.mixins import MultiLookupMixin
from .filters import ReturnPolicyFilter
from .serializers import ReturnPolicySerializer
from .models import ReturnPolicy

@extend_schema_view(
    list=extend_schema(
        tags=["Return Policy"],
        summary="Retrieve a list of Return Policy",
        description="Fetch all return Policy.",
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all Return Policy.',
                required=False,
                enum=['true', 'false']
            )
        ]
    ),
    retrieve=extend_schema(
        tags=["Return Policy"],
        summary="Retrieve a specific Return Policy",
        description="Fetch detailed information about a specific Return Policy by its ID.",
    ),
    create=extend_schema(
        tags=["Return Policy"],
        summary="Create a new Return Policy",
        description="Add a new Return Policy record.",
    ),
    update=extend_schema(
        tags=["Return Policy"],
        summary="Update an Return Policy",
        description="Modify an existing Return Policy completely.",
    ),
    partial_update=extend_schema(
        tags=["Return Policy"],
        summary="Partially update an Return Policy",
        description="Modify part of an existing Return Policy.",
    ),
    destroy=extend_schema(
        tags=["Return Policy"],
        summary="Delete an Return Policy",
        description="Remove an Return Policy by its ID.",
    ),
)
class ReturnPolicyViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = ReturnPolicy.objects.all()
    serializer_class = ReturnPolicySerializer
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
    filterset_class = ReturnPolicyFilter
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
