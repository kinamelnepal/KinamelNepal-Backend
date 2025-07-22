import django_filters
from django.db.models import Q

from .models import Product


class SlugOrIdInFilter(django_filters.BaseInFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        q_objects = Q()
        for v in value:
            if str(v).isdigit():
                q_objects |= Q(category__id=v)
            else:
                q_objects |= Q(category__slug=v)

        return qs.filter(q_objects)


class ProductFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.ChoiceFilter(choices=Product.STATUS_CHOICES)
    sale = django_filters.ChoiceFilter(field_name="sale", choices=Product.SALE_CHOICES)
    sku = django_filters.NumberFilter()
    rating = django_filters.NumberFilter()
    new_price = django_filters.NumberFilter()
    old_price = django_filters.NumberFilter()
    location = django_filters.ChoiceFilter(choices=Product.LOCATION_CHOICES)
    category = django_filters.CharFilter(method="filter_category")

    # Range filters
    new_price_range = django_filters.RangeFilter(field_name="new_price")
    old_price_range = django_filters.RangeFilter(field_name="old_price")
    quantity_range = django_filters.RangeFilter(field_name="quantity")
    weight_range = django_filters.RangeFilter(field_name="weight")
    sku_range = django_filters.RangeFilter(field_name="sku")
    rating_range = django_filters.RangeFilter(field_name="rating")
    categories = django_filters.BaseInFilter(field_name="category", lookup_expr="in")
    currency = django_filters.CharFilter(method="filter_currency")

    categories = SlugOrIdInFilter()

    def filter_category(self, queryset, name, value):
        return queryset.filter(Q(category__slug=value) | Q(category__id=value))

    def filter_currency(self, queryset, name, value):
        return queryset

    class Meta:
        model = Product
        fields = [
            "brand",
            "status",
            "new_price",
            "old_price",
            "sale",
            "sku",
            "rating",
            "location",
            "new_price_range",
            "old_price_range",
            "sku_range",
            "rating_range",
            "weight_range",
            "quantity_range",
            "category",
            "currency",
        ]
