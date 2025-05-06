from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from core.mixins import MultiLookupMixin
from .filters import CategoryFilter
from .serializers import CategorySerializer
from .models import Category
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema_view
from drf_spectacular.utils import OpenApiResponse

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
                enum=['true', 'false']
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
    bulk_create=extend_schema(
        tags=["Category"],
        summary="Bulk create categories",
        description="Create multiple categories at once.",
        request=CategorySerializer(many=True),
        responses={
            201: OpenApiResponse(
                description="Categories successfully created",
            ),
            400: OpenApiResponse(
                description="Bad Request, invalid data"
            ),
        },
    ),
)
class CategoryViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_create']:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return [AllowAny()]

    def paginate_queryset(self, queryset):
        all_param = self.request.query_params.get('all', None)
        if all_param == 'true':
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    filterset_class = CategoryFilter
    ordering_fields = ['id', 'name', 'item', 'num', 'created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create categories. Accepts a list of category data and creates all categories in one go.
        """
        try:
        
            serializer = CategorySerializer(data=request.data, many=True)
            
            if serializer.is_valid():
                categories = serializer.save()

                return Response(
                    {"message": f"{len(categories)} categories created successfully."},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except IntegrityError as e:
            return Response(
                {"error": "Integrity error occurred: " + str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
