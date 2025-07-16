from rest_framework.permissions import AllowAny, IsAdminUser

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .filters import ContactFilter
from .models import Contact
from .serializers import ContactSerializer


@generate_bulk_schema_view("Contact", ContactSerializer)
@generate_crud_schema_view("Contact")
class ContactViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filterset_class = ContactFilter
    search_fields = ["full_name", "email"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    bulk_schema_tag = "Contact"

    permission_classes_by_action = {
        "create": [AllowAny],
        "retrieve": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "list": [IsAdminUser],
        "default": [IsAdminUser],
    }
