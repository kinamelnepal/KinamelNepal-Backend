
from django.contrib import admin
from django.utils.timezone import now
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from django.utils.timesince import timesince
from django.shortcuts import get_object_or_404
from uuid import UUID
from drf_spectacular.utils import extend_schema_field, OpenApiParameter


class HideBaseModelFieldsMixin(admin.ModelAdmin):
    """
    Mixin to automatically exclude BaseModel fields from Django Admin.
    Fields like `uuid`, `slug`, `created_at`, `updated_at`, `is_deleted`, etc., 
    will be excluded in the admin view.
    """
    exclude = ('uuid', 'slug', 'created_at', 'updated_at', 'deleted_at', 'is_deleted', 'created_by', 'updated_by')
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += ('uuid', 'slug', 'created_at', 'updated_at', 'deleted_at', 'is_deleted', 'created_by', 'updated_by', 'deleted_by', 'status','version','remarks','metadata')
        return readonly_fields


class FormatBaseModelFieldsMixin(admin.ModelAdmin):
    def formatted_created_at(self, obj):
        return f"{timesince(obj.created_at, now())} ago"
    formatted_created_at.short_description = 'Created At'

    def formatted_updated_at(self, obj):
        return f"{timesince(obj.updated_at, now())} ago"
    formatted_updated_at.short_description = 'Updated At'

    def formatted_deleted_at(self, obj):
        return f"{timesince(obj.deleted_at, now())} ago"
    formatted_updated_at.short_description = 'Deleted At'


class SoftDeleteMixin:
    def delete(self, request, *args, **kwargs):
        """Soft deletes the object and returns a response."""
        instance = self.get_object() 
        instance.soft_delete()
        return Response({"detail": "Item marked as deleted."}, status=status.HTTP_204_NO_CONTENT)


class MultiLookupMixin:
    """
    A mixin to allow lookup using ID, UUID, or Slug in Django ViewSets.
    """

    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get('pk') 

        if lookup_value is None:
            raise ValueError("Lookup value cannot be None")

        if lookup_value.isdigit():
            return get_object_or_404(queryset, id=int(lookup_value))

        try:
            uuid_obj = UUID(lookup_value, version=4)
            return get_object_or_404(queryset, uuid=uuid_obj)
        except ValueError:
            pass  

        return get_object_or_404(queryset, slug=lookup_value)

    @extend_schema_field(
        OpenApiParameter(
            name="pk",
            description="Lookup user by ID (int), UUID (str), or Slug (str).",
            required=True,
            type={"oneOf": [{"type": "integer"}, {"type": "string"}]},
        )
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve user by ID, UUID, or Slug."""
        return super().retrieve(request, *args, **kwargs)
