from rest_framework.permissions import AllowAny, IsAdminUser

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import FaqFilter
from .models import Faq
from .serializers import FaqSerializer


@generate_bulk_schema_view("FAQ", FaqSerializer)
@generate_crud_schema_view("FAQ")
class FaqViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer
    filterset_class = FaqFilter
    search_fields = ["question"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    bulk_schema_tag = "FAQ"

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "default": [IsAdminUser],
    }
