import django_filters
from .models import Order, OrderItem

class OrderFilter(django_filters.FilterSet):
    order_status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    payment_method = django_filters.ChoiceFilter(choices=Order.PAYMENT_METHOD_CHOICES)
    payment_status = django_filters.ChoiceFilter(choices=Order.PAYMENT_STATUS_CHOICES)

    # Range filters
    total_range = django_filters.RangeFilter(field_name='total')
    shipping_cost_range = django_filters.RangeFilter(field_name='shipping_cost')
    tax_range = django_filters.RangeFilter(field_name='tax')
    discount_range = django_filters.RangeFilter(field_name='discount')

    # Foreign Key Filters
    shipping_address = django_filters.NumberFilter(field_name='shipping_address__id')
    billing_address = django_filters.NumberFilter(field_name='billing_address__id')
    user_id = django_filters.NumberFilter(field_name='user__id')
    class Meta:
        model = Order
        fields = [
            'order_status', 'payment_method', 'payment_status', 
            'total_range', 'shipping_cost_range', 'tax_range', 
            'discount_range', 'shipping_address', 'billing_address',
            'user_id'
        ]

class OrderItemFilter(django_filters.FilterSet):
    order = django_filters.NumberFilter(field_name='order__id')
    product = django_filters.NumberFilter(field_name='product__id')
    quantity = django_filters.NumberFilter()
    price = django_filters.NumberFilter()
    discount = django_filters.NumberFilter()
    total = django_filters.NumberFilter()

    # Range filters
    total_range = django_filters.RangeFilter(field_name='total')
    quantity_range = django_filters.RangeFilter(field_name='quantity')
    price_range = django_filters.RangeFilter(field_name='price')
    discount_range = django_filters.RangeFilter(field_name='discount')

    class Meta:
        model = OrderItem
        fields = [
            'order', 'product', 'quantity', 'price', 'discount', 'total', 
            'total_range', 'quantity_range', 'price_range', 'discount_range'
        ]
