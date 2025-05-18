from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter
)
from core.mixins import MultiLookupMixin
from .filters import CartFilter
from .serializers import CartSerializer
from .models import Cart
from rest_framework.decorators import action
from .filters import CartItemFilter
from .serializers import CartItemSerializer
from .models import CartItem

@extend_schema_view(
    list=extend_schema(
        tags=["Cart"],
        summary="Retrieve a list of carts",
        description="Fetch all carts available in the system.",
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all carts.',
                required=False,
                enum=['true', 'false'],
            ),
            OpenApiParameter(
                name='currency',
                type=str,
                description='Convert price fields to this currency (USD, EUR, NPR). Default is USD.',
                required=False,
                enum=['USD', 'EUR', 'NPR'],
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Cart"],
        summary="Retrieve a specific cart",
        description="Fetch detailed information about a specific cart by its ID.",
    ),
    create=extend_schema(
        tags=["Cart"],
        summary="Create a new cart",
        description="Create a new shopping cart.",
    ),
    update=extend_schema(
        tags=["Cart"],
        summary="Update a cart",
        description="Completely update a cart.",
    ),
    partial_update=extend_schema(
        tags=["Cart"],
        summary="Partially update a cart",
        description="Partially update cart details.",
    ),
    destroy=extend_schema(
        tags=["Cart"],
        summary="Delete a cart",
        description="Delete a cart from the system by its ID.",
    ),
)
class CartViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_permissions(self):
            return [AllowAny()]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CartFilter
    search_fields = ['user__first_name','user__last_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def paginate_queryset(self, queryset):
        """
        Override paginate_queryset to check for 'all=true' query parameter.
        """
        all_param = self.request.query_params.get('all', None)
        if all_param == 'true':
            return None
        return super().paginate_queryset(queryset)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        currency = self.request.query_params.get('currency', 'NPR')
        context['currency'] = currency
        return context


    @extend_schema(
        tags=["Cart"],
        summary="Bulk Insert Carts",
        description="Insert multiple carts into the system in a single request.",
        request=CartSerializer(many=True),
    )
    @action(detail=False, methods=['post'])
    def bulk_insert(self, request, *args, **kwargs):
        """
        Bulk insert carts into the system.
        Accepts a list of carts to insert.
        """
        carts_data = request.data
        
        if not isinstance(carts_data, list) or len(carts_data) == 0:
            return Response(
                {"detail": "Expected 'carts' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CartSerializer(data=carts_data, many=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"{len(carts_data)} carts successfully inserted."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )



@extend_schema_view(
    list=extend_schema(
        tags=["CartItem"],
        summary="Retrieve a list of cart items",
        description="Fetch all cart items associated with a cart.",
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all cart items.',
                required=False,
                enum=['true', 'false'],
            ),
            OpenApiParameter(
                name='currency',
                type=str,
                description='Convert price fields to this currency (USD, EUR, NPR). Default is USD.',
                required=False,
                enum=['NPR','USD', 'EUR'],
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["CartItem"],
        summary="Retrieve a specific cart item",
        description="Fetch detailed information about a specific cart item by its ID.",
    ),
    create=extend_schema(
        tags=["CartItem"],
        summary="Create a new cart item",
        description="Add a new item to a cart.",
    ),
    update=extend_schema(
        tags=["CartItem"],
        summary="Update a cart item",
        description="Completely update a cart item.",
    ),
    partial_update=extend_schema(
        tags=["CartItem"],
        summary="Partially update a cart item",
        description="Partially update cart item details.",
    ),
    destroy=extend_schema(
        tags=["CartItem"],
        summary="Delete a cart item",
        description="Delete a cart item from the cart.",
    ),
)




class CartItemViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_permissions(self):
            return [AllowAny()]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CartItemFilter
    search_fields = ['product__title','cart__user__first_name','cart__user__last_name']
    ordering_fields = ['created_at', 'updated_at', 'product__title', 'quantity']
    ordering = ['product_title']

    def paginate_queryset(self, queryset):
        """
        Override paginate_queryset to check for 'all=true' query parameter.
        """
        all_param = self.request.query_params.get('all', None)
        if all_param == 'true':
            return None
        return super().paginate_queryset(queryset)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Get the currency query param
        currency = self.request.query_params.get('currency', 'NPR').upper()
        context['currency'] = currency
        return context

    @extend_schema(
        tags=["CartItem"],
        summary="Bulk Insert Cart Items",
        description="Insert multiple cart items into the system in a single request.",
        request=CartItemSerializer(many=True),
    )
    @action(detail=False, methods=['post'])
    def bulk_insert(self, request, *args, **kwargs):
        """
        Bulk insert cart items into the system.
        Accepts a list of cart items to insert.
        """
        cart_items_data = request.data
        
        if not isinstance(cart_items_data, list) or len(cart_items_data) == 0:
            return Response(
                {"detail": "Expected 'cart_items' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CartItemSerializer(data=cart_items_data, many=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"{len(cart_items_data)} cart items successfully inserted."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
