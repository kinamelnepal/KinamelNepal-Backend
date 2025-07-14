from rest_framework.permissions import AllowAny, IsAdminUser

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import PrivacyPolicyFilter
from .models import PrivacyPolicy
from .serializers import PrivacyPolicySerializer


@generate_bulk_schema_view("Privacy Policy", PrivacyPolicySerializer)
@generate_crud_schema_view("Privacy Policy")
class PrivacyPolicyViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = PrivacyPolicy.objects.all()
    serializer_class = PrivacyPolicySerializer
    filterset_class = PrivacyPolicyFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    bulk_schema_tag = "Privacy Policy"

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "bulk_create": [IsAdminUser],
        "bulk_update": [IsAdminUser],
        "bulk_delete": [IsAdminUser],
        "default": [IsAdminUser],
    }
