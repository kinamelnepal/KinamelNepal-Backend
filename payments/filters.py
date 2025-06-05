import django_filters
from .models import Payment

class PaymentFilter(django_filters.FilterSet):
    # Choice filters for method and status
    method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHOD_CHOICES)
    payment_status = django_filters.ChoiceFilter(choices=Payment.STATUS_CHOICES)

    # Range filters for amounts
    amount_range = django_filters.RangeFilter(field_name='amount')
    tax_amount_range = django_filters.RangeFilter(field_name='tax_amount')
    total_amount_range = django_filters.RangeFilter(field_name='total_amount')

    # Filtering by related order
    order_id = django_filters.NumberFilter(field_name='order__id')

    # Datetime filters
    paid_at = django_filters.DateTimeFilter(field_name='paid_at')
    paid_at_range = django_filters.DateFromToRangeFilter(field_name='paid_at')

    class Meta:
        model = Payment
        fields = [
            'method',
            'payment_status',
            'order_id',
            'amount_range',
            'tax_amount_range',
            'total_amount_range',
            'paid_at',
            'paid_at_range',
        ]
