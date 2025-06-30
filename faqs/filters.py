import django_filters

from .models import Faq


class FaqFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter()
    created_at_range = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Faq
        fields = ["created_at", "created_at_range"]
