from rest_framework import serializers
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from drf_spectacular.utils import extend_schema_serializer

# class GeoLocationSerializer(serializers.Serializer):
#     latitude = serializers.FloatField()
#     longitude = serializers.FloatField()

@extend_schema_serializer(
    exclude_fields=['uuid', 'slug', 'status', 'remarks', 'version', 'metadata', 'is_deleted', 'created_by', 'updated_by', 'deleted_by']
)
class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    # Define base fields to be removed
    base_model_fields = {
        'uuid', 'slug', 'created_at', 'updated_at', 'deleted_at',
        'is_deleted', 'created_by', 'updated_by', 'deleted_by',
        'status', 'remarks', 'version', 'metadata'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove base model fields for write operations (except for GET)
        request = self.context.get('request')
        is_schema = self.context.get('swagger_fake_view', False)

        if not is_schema and request and request.method in {'POST', 'PUT', 'PATCH'}:
            for field in self.base_model_fields:
                self.fields.pop(field, None)

    def get_fields(self):
        fields = super().get_fields()
        swagger = self.context.get('swagger_fake_view', False)
        if swagger:
            for field in self._base_model_fields:
                fields.pop(field, None)
        return fields

    def validate(self, attrs):
        model = self.Meta.model

        # Get unique fields directly from the model class (without using Meta)
        model_unique_fields = getattr(model, 'unique_fields', [])

        # Get base_unique_fields from the base model (similar to before)
        base_unique_fields = getattr(model.__base__, 'unique_fields', [])
        print(f"Model: {model.__name__}, Model Unique Fields: {model_unique_fields}, Base Unique Fields: {base_unique_fields}")

        # --------------------------
        # 1. Validate model_unique_fields (within this model)
        for field in model_unique_fields:
            value = attrs.get(field)
            if value is None:
                continue

            qs = model.objects.filter(**{field: value}, is_deleted=False)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError({
                    field: f"{field.title()} '{value}' already exists in '{model.__name__}'"
                })

        # --------------------------
        # 2. Validate base_unique_fields (across all BaseModel subclasses)
        for field in base_unique_fields:
            value = attrs.get(field)
            if value is None:
                continue

            # Create a Q object to build a query condition to check across all models inheriting from BaseModel
            condition = Q(**{field: value, 'is_deleted': False})

            # Check all models that are subclasses of BaseModel
            for other_model in apps.get_models():
                if not issubclass(other_model, model.__base__):
                    continue

                # Skip models that don't have the field
                try:
                    other_model._meta.get_field(field)
                except FieldDoesNotExist:
                    continue

                # Query the model for the field's uniqueness
                qs = other_model.objects.filter(condition)
                if self.instance and isinstance(self.instance, other_model):
                    qs = qs.exclude(pk=self.instance.pk)

                if qs.exists():
                    raise serializers.ValidationError({
                        field: f"{field.title()} '{value}' already exists in '{other_model.__name__}'"
                    })

        return super().validate(attrs)


