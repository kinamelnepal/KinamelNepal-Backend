from rest_framework.permissions import AllowAny, IsAdminUser

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import TermsAndConditionsFilter
from .models import TermsAndConditions
from .serializers import TermsAndConditionsSerializer


@generate_bulk_schema_view("Terms and Conditions", TermsAndConditionsSerializer)
@generate_crud_schema_view("Terms and Conditions")
class TermsAndConditionsViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = TermsAndConditions.objects.all()
    serializer_class = TermsAndConditionsSerializer
    filterset_class = TermsAndConditionsFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    bulk_schema_tag = "Terms and Conditions"

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "default": [IsAdminUser],
    }
