import django_filters
from .models import Banner

class BannerFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Banner.STATUS_CHOICES)
    display_location = django_filters.ChoiceFilter(choices=Banner.DISPLAY_LOCATION_CHOICES)
    start_date = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='lte')
    display_order = django_filters.NumberFilter()

    start_date_range = django_filters.DateRangeFilter(field_name='start_date')
    end_date_range = django_filters.DateRangeFilter(field_name='end_date')
    show_call_to_action = django_filters.BooleanFilter(field_name='show_call_to_action')
    class Meta:
        model = Banner
        fields = ['status', 'display_location', 'start_date', 'end_date', 'display_order', 'start_date_range', 'end_date_range']
