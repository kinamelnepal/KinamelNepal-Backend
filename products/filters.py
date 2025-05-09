import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr='iexact')
    status = django_filters.ChoiceFilter(choices=Product.STATUS_CHOICES)
    # sale = django_filters.ChoiceFilter(choices=Product.SALE_CHOICES)
    sale = django_filters.ChoiceFilter(field_name='sale', choices=Product.SALE_CHOICES)

    sku = django_filters.NumberFilter()
    rating = django_filters.NumberFilter()
    new_price = django_filters.NumberFilter()
    old_price = django_filters.NumberFilter()
    location = django_filters.ChoiceFilter(choices=Product.LOCATION_CHOICES)
    category= django_filters.CharFilter(field_name='category', lookup_expr='exact')

    # Adding range filters for these fields
    new_price_range = django_filters.RangeFilter(field_name='new_price')
    old_price_range = django_filters.RangeFilter(field_name='old_price')
    quantity_range = django_filters.RangeFilter(field_name='quantity')
    weight_range = django_filters.RangeFilter(field_name='weight')
    sku_range = django_filters.RangeFilter(field_name='sku')
    rating_range = django_filters.RangeFilter(field_name='rating')

    class Meta:
        model = Product
        fields = ['brand', 'status', 'new_price', 'old_price', 'sale', 'sku', 'rating',  'location', 'new_price_range', 'old_price_range', 'sku_range', 'rating_range','weight_range','quantity_range','category']
