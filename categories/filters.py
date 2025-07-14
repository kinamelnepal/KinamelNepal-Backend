import django_filters

from .models import Category


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="iexact")
    persantine = django_filters.CharFilter(lookup_expr="iexact")
    item = django_filters.RangeFilter()
    num = django_filters.RangeFilter()

    class Meta:
        model = Category
        fields = ["name", "persantine", "item", "num"]
