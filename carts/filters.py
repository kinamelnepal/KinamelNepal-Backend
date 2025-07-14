import django_filters

from .models import Cart, CartItem


class CartFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__id", lookup_expr="iexact")
    # status = django_filters.ChoiceFilter(field_name='status', choices=Cart.STATUS_CHOICES)
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Cart
        fields = ["user", "status", "created_at", "updated_at"]


class CartItemFilter(django_filters.FilterSet):
    cart = django_filters.UUIDFilter(field_name="cart__uuid")
    user = django_filters.NumberFilter(field_name="cart__user")
    product = django_filters.CharFilter(
        field_name="product__title", lookup_expr="icontains"
    )
    product_sku = django_filters.NumberFilter(field_name="product__sku")
    quantity = django_filters.NumberFilter()
    quantity_range = django_filters.RangeFilter(field_name="quantity")
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    currency = django_filters.CharFilter(method="filter_currency")

    def filter_currency(self, queryset, name, value):
        return queryset

    class Meta:
        model = CartItem
        fields = [
            "cart",
            "product",
            "product_sku",
            "quantity",
            "quantity_range",
            "user",
            "created_at",
            "updated_at",
            "currency",
        ]
