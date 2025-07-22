import random
import threading

from django.core.exceptions import ImproperlyConfigured
from drf_spectacular import utils as spectacular_utils
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers


def generate_4_digit_unique_pass_code(model):

    while True:
        pass_code = random.randint(1000, 9999)
        if not model.objects.filter(pass_code=pass_code).exists():
            return pass_code


_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, "user", None)


def set_current_user(user):
    _thread_locals.user = user


def generate_bulk_update_serializer(base_serializer_class):
    """
    Dynamically creates a serializer class for bulk update
    by extending the base serializer and adding 'id' as a required field.
    Avoids schema name collisions in drf-spectacular.
    """
    class_name = f"{base_serializer_class.__name__.replace('Serializer', '')}BulkUpdateSerializer"

    # ✅ Safely get Meta.fields
    base_fields = getattr(base_serializer_class.Meta, "fields", None)
    if base_fields is None:
        raise ImproperlyConfigured("Bulk update serializer requires `fields` in Meta.")

    base_fields = list(base_fields)
    if "id" not in base_fields:
        base_fields.insert(0, "id")

    # ✅ Define Meta class using already-evaluated `base_fields`
    class Meta(base_serializer_class.Meta):
        fields = base_fields

    # ✅ Create new serializer class with custom Meta and id field
    serializer_class = type(
        class_name,
        (base_serializer_class,),
        {
            "id": serializers.IntegerField(),
            "Meta": Meta,
            "__module__": base_serializer_class.__module__,
        },
    )

    # ✅ Helpful for DRF Spectacular schema generation
    serializer_class._spectacular_serializer_name = class_name

    return serializer_class


class BulkDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of IDs to delete",
    )


def generate_bulk_schema_view(tag, serializer_class):
    """
    Reusable decorator to add bulk operation schema documentation
    to any viewset that mixes in bulk_create, bulk_update, and bulk_delete.
    """

    def decorator(cls):
        bulk_update_serializer = generate_bulk_update_serializer(serializer_class)

        return extend_schema_view(
            bulk_create=extend_schema(
                request=serializer_class(many=True),
                tags=[tag],
                summary=f"Bulk creates {tag.lower()}",
            ),
            bulk_update=extend_schema(
                request=bulk_update_serializer(many=True),
                tags=[tag],
                summary=f"Bulk update {tag.lower()}",
            ),
            bulk_delete=extend_schema(
                request=BulkDeleteSerializer,
                tags=[tag],
                summary=f"Bulk delete {tag.lower()}",
            ),
        )(cls)

    return decorator


def generate_crud_schema_view(tag):
    return extend_schema_view(
        list=extend_schema(
            tags=[tag],
            summary=f"Retrieve a list of {tag.lower()}",
            description=f"Fetch all {tag.lower()}s.",
            parameters=[
                spectacular_utils.OpenApiParameter(
                    name="all",
                    type=str,
                    description="If set to `true`, disables pagination.",
                    required=False,
                    enum=["true", "false"],
                )
            ],
        ),
        retrieve=extend_schema(
            tags=[tag],
            summary=f"Retrieve a specific {tag.lower()}",
            description=f"Fetch detailed info about a specific {tag.lower()}.",
        ),
        create=extend_schema(
            tags=[tag],
            summary=f"Create a new {tag.lower()}",
            description=f"Add a new {tag.lower()}.",
        ),
        update=extend_schema(
            tags=[tag],
            summary=f"Update a {tag.lower()}",
            description=f"Completely update an existing {tag.lower()}.",
        ),
        partial_update=extend_schema(
            tags=[tag],
            summary=f"Partially update a {tag.lower()}",
            description=f"Partially update an existing {tag.lower()}.",
        ),
        destroy=extend_schema(
            tags=[tag],
            summary=f"Delete a {tag.lower()}",
            description=f"Remove a {tag.lower()} by ID.",
        ),
    )
