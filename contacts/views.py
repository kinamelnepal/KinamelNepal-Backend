from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from core.mixins import MultiLookupMixin
from .filters import ContactFilter
from .serializers import ContactSerializer
from .models import Contact


@extend_schema_view(
    list=extend_schema(
        tags=["Contact"],
        summary="Retrieve a list of contact messages",
        description="Fetch all contact form submissions.",
        parameters=[
            OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all contact messages.',
                required=False,
                enum=['true', 'false']
            )
        ]
    ),
    retrieve=extend_schema(
        tags=["Contact"],
        summary="Retrieve a specific contact message",
        description="Fetch detailed information about a specific contact form submission.",
    ),
    create=extend_schema(
        tags=["Contact"],
        summary="Submit a contact message",
        description="Submit a message via the contact form.",
    ),
    update=extend_schema(
        tags=["Contact"],
        summary="Update a contact's details",
        description="Modify an existing contact's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Contact"],
        summary="Partially update a contact's details",
        description="Modify some fields of an existing contact (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Contact"],
        summary="Delete a contact message",
        description="Remove a contact message by its ID.",
    ),
)
class ContactViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def paginate_queryset(self, queryset):
        all_param = self.request.query_params.get('all', None)
        if all_param == 'true':
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContactFilter
    search_fields = ['full_name', 'email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
