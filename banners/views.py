from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import BannerFilter
from .models import Banner
from .serializers import BannerSerializer


@generate_bulk_schema_view("Banner", BannerSerializer)
@generate_crud_schema_view("Banner")
class BannerViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    filterset_class = BannerFilter
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    bulk_schema_tag = "Banner"

    search_fields = ["title", "subtitle"]
    ordering_fields = ["id", "display_order", "status", "start_date", "end_date"]
    ordering = ["display_order", "-start_date"]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    permission_classes_by_action = {
        "bulk_create": [IsAuthenticated, IsAdminUser],
        "create": [IsAuthenticated, IsAdminUser],
        "update": [IsAuthenticated, IsAdminUser],
        "partial_update": [IsAuthenticated, IsAdminUser],
        "destroy": [IsAuthenticated, IsAdminUser],
        "retrieve": [AllowAny],
        "list": [AllowAny],
        "default": [AllowAny],
    }
