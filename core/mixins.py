from uuid import UUID

from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.utils.timesince import timesince
from django.utils.timezone import now
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_field,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


class HideBaseModelFieldsMixin(admin.ModelAdmin):
    """
    Mixin to automatically exclude BaseModel fields from Django Admin.
    Fields like `uuid`, `slug`, `created_at`, `updated_at`, `is_deleted`, etc.,
    will be excluded in the admin view.
    """

    exclude = (
        "uuid",
        "slug",
        "created_at",
        "updated_at",
        "deleted_at",
        "is_deleted",
        "created_by",
        "updated_by",
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += (
            "uuid",
            "slug",
            "created_at",
            "updated_at",
            "deleted_at",
            "is_deleted",
            "created_by",
            "updated_by",
            "deleted_by",
            "status",
            "version",
            "remarks",
            "metadata",
        )
        return readonly_fields


class FormatBaseModelFieldsMixin(admin.ModelAdmin):
    def formatted_created_at(self, obj):
        return f"{timesince(obj.created_at, now())} ago"

    formatted_created_at.short_description = "Created At"

    def formatted_updated_at(self, obj):
        return f"{timesince(obj.updated_at, now())} ago"

    formatted_updated_at.short_description = "Updated At"

    def formatted_deleted_at(self, obj):
        return f"{timesince(obj.deleted_at, now())} ago"

    formatted_updated_at.short_description = "Deleted At"


class SoftDeleteMixin:
    def delete(self, request, *args, **kwargs):
        """Soft deletes the object and returns a response."""
        instance = self.get_object()
        instance.soft_delete()
        return Response(
            {"detail": "Item marked as deleted."}, status=status.HTTP_204_NO_CONTENT
        )


class MultiLookupMixin:
    """
    A mixin to allow lookup using ID, UUID, or Slug in Django ViewSets.
    """

    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get("pk")

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


class BulkOperationsMixin:
    bulk_schema_tag = None

    def get_model(self):
        return self.get_queryset().model

    def get_bulk_tag(self):
        return [self.bulk_schema_tag or self.__class__.__name__]

    def get_bulk_update_serializer(self):
        base_serializer = self.get_serializer().__class__
        fields = base_serializer().get_fields()
        fields["id"] = serializers.IntegerField()
        return type("BulkUpdateSerializer", (serializers.Serializer,), fields)

    @extend_schema(
        summary="Bulk create",
        description="Create multiple records at once.",
        tags=None,
        responses={201: OpenApiResponse(description="Created successfully")},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-create",
        permission_classes=[IsAdminUser],
    )
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.get_model().objects.bulk_create(
            [self.get_model()(**item) for item in serializer.validated_data]
        )
        return Response({"message": "Bulk create successful"}, status=201)

    @extend_schema(
        summary="Bulk update",
        description="Update multiple records at once.",
        tags=None,
        request=None,
        responses={200: OpenApiResponse(description="Updated successfully")},
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="bulk-update",
        permission_classes=[IsAdminUser],
    )
    def bulk_update(self, request):
        serializer_class = self.get_bulk_update_serializer()
        serializer = serializer_class(data=request.data, many=True, partial=True)
        serializer.is_valid(raise_exception=True)

        model = self.get_model()
        updated = 0
        for item in serializer.validated_data:
            obj = model.objects.filter(id=item.get("id")).first()
            if obj:
                serializer = self.get_serializer(obj, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated += 1

        return Response({"message": "Bulk update successful", "updated_count": updated})

    @extend_schema(
        summary="Bulk delete",
        description="Delete multiple records by ID.",
        tags=None,
        request=inline_serializer(
            name="BulkDeleteInput",
            fields={"ids": serializers.ListField(child=serializers.IntegerField())},
        ),
        responses={200: OpenApiResponse(description="Deleted successfully")},
    )
    @action(
        detail=False,
        methods=["delete"],
        url_path="bulk-delete",
        permission_classes=[IsAdminUser],
    )
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        deleted, _ = self.get_model().objects.filter(id__in=ids).delete()
        return Response({"message": "Bulk delete successful", "deleted_count": deleted})
