import django_filters
from .models import Address


class AddressFilter(django_filters.FilterSet):
    address_type = django_filters.ChoiceFilter(choices=Address.ADDRESS_TYPE_CHOICES)
    is_default = django_filters.BooleanFilter()
    user = django_filters.NumberFilter(field_name='user__id')
    city = django_filters.CharFilter()
    state = django_filters.CharFilter()
    country = django_filters.CharFilter()

    class Meta:
        model = Address
        fields = [
            'address_type', 'is_default', 'user',
            'city', 'state', 'country'
        ]
