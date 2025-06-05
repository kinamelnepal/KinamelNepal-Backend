from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
from core.mixins import MultiLookupMixin
from .filters import OrderFilter, OrderItemFilter
from .serializers import OrderSerializer, OrderItemSerializer
from .models import Order, OrderItem
from rest_framework.decorators import action
from payments.serializers import PaymentSerializer
from payments.utils import initiate_esewa_payment,build_esewa_payment_url

@extend_schema_view(
    list=extend_schema(
         parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all products.',
                required=False,
                enum=['true', 'false']  
            ),
            OpenApiParameter(
                name='currency',
                type=str,
                description='Convert price fields to this currency (USD, EUR, NPR). Default is USD.',
                required=False,
                
                enum= ['NPR','USD', 'EUR'],
            ),

        ],
        tags=["Order"],
        summary="Retrieve a list of orders",
        description="Fetch all orders available in the system.",
    ),
    retrieve=extend_schema(
        tags=["Order"],
        summary="Retrieve a specific order",
        description="Fetch detailed information about a specific order by its ID.",
    ),
    create=extend_schema(
        tags=["Order"],
        summary="Create a new order",
        description="Create a new order with the required details.",
    ),
    update=extend_schema(
        tags=["Order"],
        summary="Update an order's details",
        description="Modify an existing order's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Order"],
        summary="Partially update an order's details",
        description="Modify some fields of an existing order (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Order"],
        summary="Delete an order",
        description="Remove an order from the system by its ID.",
    ),
)
class OrderViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['full_name', 'email', 'phone_number']
    ordering_fields = ['total', 'order_status', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
            return [IsAuthenticated()]

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
        currency = self.request.query_params.get('currency', 'NPR').upper()
        context['currency'] = currency
        return context
    

    @extend_schema(
        tags=["Order"],
        summary="Bulk Insert Orders",
        description="Insert multiple orders into the system in a single request.",
        request=OrderSerializer(many=True),
    )
    @action(detail=False, methods=['post'])
    def bulk_insert(self, request, *args, **kwargs):
        """
        Bulk insert orders into the system.
        Accepts a list of orders to insert.
        """
        orders_data = request.data
        
        if not isinstance(orders_data, list) or len(orders_data) == 0:
            return Response(
                {"detail": "Expected 'orders' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderSerializer(data=orders_data, many=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"{len(orders_data)} orders successfully inserted."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all products.',
                required=False,
                enum=['true', 'false']  
            ),
            OpenApiParameter(
                name='currency',
                type=str,
                description='Convert price fields to this currency (USD, EUR, NPR). Default is USD.',
                required=False,
                
                enum= ['NPR','USD', 'EUR'],
            ),

        ],
        tags=["OrderItem"],
        summary="Retrieve a list of order items",
        description="Fetch all order items for orders in the system.",
    ),
    retrieve=extend_schema(
        tags=["OrderItem"],
        summary="Retrieve a specific order item",
        description="Fetch detailed information about a specific order item by its ID.",
    ),
    create=extend_schema(
        tags=["OrderItem"],
        summary="Create a new order item",
        description="Create a new order item with the required details.",
    ),
    update=extend_schema(
        tags=["OrderItem"],
        summary="Update an order item's details",
        description="Modify an existing order item's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["OrderItem"],
        summary="Partially update an order item's details",
        description="Modify some fields of an existing order item (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["OrderItem"],
        summary="Delete an order item",
        description="Remove an order item from the system by its ID.",
    ),
)

class OrderItemViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderItemFilter
    ordering_fields = ['total', 'quantity', 'price']
    ordering = ['-total']


    def get_permissions(self):
            return [IsAuthenticated()]

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
        print(self.request.query_params.get('currency'),'the currency')
        currency = self.request.query_params.get('currency', 'NPR').upper()
        context['currency'] = currency
        return context