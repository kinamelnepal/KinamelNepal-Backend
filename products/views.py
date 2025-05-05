from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
from core.mixins import MultiLookupMixin
from .filters import ProductFilter
from .serializers import ProductSerializer
from .models import Product
from rest_framework.decorators import action

@extend_schema_view(
    list=extend_schema(
        tags=["Product"],
        summary="Retrieve a list of products",
        description="Fetch all products available in the system.",
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all products.',
                required=False,
                enum=['true', 'false']  
            )
        ]
    ),
    retrieve=extend_schema(
        tags=["Product"],
        summary="Retrieve a specific product",
        description="Fetch detailed information about a specific product by its ID.",
    ),
    create=extend_schema(
        tags=["Product"],
        summary="Create a new product",
        description="Create a new product with the required details.",
    ),
    update=extend_schema(
        tags=["Product"],
        summary="Update a product's details",
        description="Modify an existing product's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Product"],
        summary="Partially update a product's details",
        description="Modify some fields of an existing product (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Product"],
        summary="Delete a product",
        description="Remove a product from the system by its ID.",
    ),
)
class ProductViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
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
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['title', 'brand'] 
    filterset_class = ProductFilter
    ordering_fields = ['id', 'new_price', 'old_price', 'rating', 'sku', 'created_at', 'updated_at','quantity','weight']
    ordering = ['-created_at']  

    @extend_schema(
        tags=["Product"],
        summary="Bulk Insert Products",
        description="Insert multiple products into the system in a single request.",
        request=ProductSerializer(many=True),
        # responses={
        #     201: OpenApiResponse(
        #         description="Bulk insert successful",
        #         content={"application/json": {"example": {"detail": "2 products successfully inserted."}}}
        #     ),
        #     400: OpenApiResponse(
        #         description="Invalid input",
        #         content={"application/json": {"example": {"detail": "Expected 'products' to be a non-empty list."}}}
        #     ),
        # }
    )
    @action(detail=False, methods=['post'])
    def bulk_insert(self, request, *args, **kwargs):
        """
        Bulk insert products into the system.
        Accepts a list of products to insert.
        """
        products_data = request.data
        
        if not isinstance(products_data, list) or len(products_data) == 0:
            return Response(
                {"detail": "Expected 'products' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ProductSerializer(data=products_data, many=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"{len(products_data)} products successfully inserted."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )