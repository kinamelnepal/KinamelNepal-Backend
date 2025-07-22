from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from .models import APIKey


class GeoLocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


@extend_schema_serializer(
    exclude_fields=[
        "uuid",
        "slug",
        "status",
        "remarks",
        "version",
        "metadata",
        "is_deleted",
        "created_by",
        "updated_by",
        "deleted_by",
    ]
)
class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    # Define base fields to be removed
    base_model_fields = {
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
        "remarks",
        "version",
        "metadata",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove base model fields for write operations (except for GET)
        request = self.context.get("request")
        is_schema = self.context.get("swagger_fake_view", False)

        if not is_schema and request and request.method in {"POST", "PUT", "PATCH"}:
            for field in self.base_model_fields:
                self.fields.pop(field, None)

    def get_fields(self):
        fields = super().get_fields()
        swagger = self.context.get("swagger_fake_view", False)
        if swagger:
            for field in self._base_model_fields:
                fields.pop(field, None)
        return fields

    def validate(self, attrs):
        model = self.Meta.model

        model_unique_fields = getattr(model, "unique_fields", [])
        base_unique_fields = getattr(model.__base__, "unique_fields", [])
        print(
            f"Model: {model.__name__}, Model Unique Fields: {model_unique_fields}, Base Unique Fields: {base_unique_fields}"
        )

        self._validate_model_unique_fields(model, attrs, model_unique_fields)
        self._validate_base_unique_fields(model, attrs, base_unique_fields)

        return super().validate(attrs)

    def _validate_model_unique_fields(self, model, attrs, unique_fields):
        for field in unique_fields:
            value = attrs.get(field)
            if value is None:
                continue

            qs = model.objects.filter(**{field: value}, is_deleted=False)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError(
                    {
                        field: f"{field.title()} '{value}' already exists in '{model.__name__}'"
                    }
                )

    def _validate_base_unique_fields(self, model, attrs, base_unique_fields):
        for field in base_unique_fields:
            value = attrs.get(field)
            if value is None:
                continue

            condition = Q(**{field: value, "is_deleted": False})
            self._check_field_in_other_models(model, field, value, condition)

    def _check_field_in_other_models(self, model, field, value, condition):
        for other_model in apps.get_models():
            if not issubclass(other_model, model.__base__):
                continue

            if not self._model_has_field(other_model, field):
                continue

            qs = other_model.objects.filter(condition)
            if self.instance and isinstance(self.instance, other_model):
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError(
                    {
                        field: f"{field.title()} '{value}' already exists in '{other_model.__name__}'"
                    }
                )

    def _model_has_field(self, model, field):
        try:
            model._meta.get_field(field)
            return True
        except FieldDoesNotExist:
            return False


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ["id", "name", "key", "is_active", "created_at"]
        read_only_fields = ["id", "key", "created_at"]

    def create(self, validated_data):
        return super().create(validated_data)
