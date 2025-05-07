import django_filters
from .models import Blog

class BlogFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    date = django_filters.DateFilter(field_name='date')
    date_range = django_filters.DateFromToRangeFilter(field_name='date')

    class Meta:
        model = Blog
        fields = ['category', 'date', 'date_range']
