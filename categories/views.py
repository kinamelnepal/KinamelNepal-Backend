from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
from core.mixins import MultiLookupMixin
from .filters import CategoryFilter
from .serializers import CategorySerializer
from .models import Category

@extend_schema_view(
    list=extend_schema(
        tags=["Category"],
        summary="Retrieve a list of categories",
        description="Fetch all categories available in the system.",
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all categories.',
                required=False,
                enum=['true', 'false']  # Optional: You can specify allowed values
            )
        ]
    ),
    retrieve=extend_schema(
        tags=["Category"],
        summary="Retrieve a specific category",
        description="Fetch detailed information about a specific category by its ID.",
    ),
    create=extend_schema(
        tags=["Category"],
        summary="Create a new category",
        description="Create a new category with the required details.",
    ),
    update=extend_schema(
        tags=["Category"],
        summary="Update a category's details",
        description="Modify an existing category's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Category"],
        summary="Partially update a category's details",
        description="Modify some fields of an existing category (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Category"],
        summary="Delete a category",
        description="Remove a category from the system by its ID.",
    ),
)
class CategoryViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return [AllowAny()]

    def paginate_queryset(self, queryset):
        """
        Override paginate_queryset to check for 'all=true' query parameter.
        """
        all_param = self.request.query_params.get('all', None)
        if all_param == 'true':
            # If 'all=true', return the full queryset without pagination
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['name']  # Removed 'persantine' from search_fields
    filterset_class = CategoryFilter
    ordering_fields = ['id', 'name', 'item', 'num', 'created_at', 'updated_at']  # Added 'id' to ordering_fields
    ordering = ['-created_at']
