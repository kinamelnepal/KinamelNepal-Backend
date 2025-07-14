from rest_framework.permissions import AllowAny, IsAdminUser

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import ReturnPolicyFilter
from .models import ReturnPolicy
from .serializers import ReturnPolicySerializer


@generate_bulk_schema_view("Return Policy", ReturnPolicySerializer)
@generate_crud_schema_view("Return Policy")
class ReturnPolicyViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = ReturnPolicy.objects.all()
    serializer_class = ReturnPolicySerializer
    filterset_class = ReturnPolicyFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    bulk_schema_tag = "Return Policy"

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "default": [IsAdminUser],
    }
