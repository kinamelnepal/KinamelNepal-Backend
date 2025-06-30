import secrets
import uuid

from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils import timezone
from django.utils.text import slugify

from .managers import BaseModelManager
from .utils import get_current_user


class BaseModel(models.Model):
    objects = BaseModelManager()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(blank=True, null=True, editable=False, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        editable=False,
    )
    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        editable=False,
    )
    deleted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("archived", "Archived"),
        ],
        default="active",
    )
    remarks = models.TextField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(blank=True, null=True)
    unique_fields = ["slug", "uuid"]

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        user = get_current_user()

        if not self.slug:
            self.slug = slugify(str(self.uuid))

        if self.pk is None:
            if user and user.is_authenticated:
                self.created_by = user
        else:
            if user and user.is_authenticated:
                self.updated_by = user

        self.version += 1
        super().save(*args, **kwargs)

    def cascade_or_nullify(self):
        """Handle related objects based on on_delete behavior (CASCADE or SET_NULL)."""
        for related_object in self._meta.related_objects:
            model = related_object.related_model
            related_field_name = related_object.field.name  # FK field on related model
            on_delete_behavior = related_object.field.remote_field.on_delete

            filter_kwargs = {related_field_name: self}
            related_qs = model._default_manager.filter(**filter_kwargs)

            for related_obj in related_qs:
                if not hasattr(related_obj, "is_deleted") or related_obj.is_deleted:
                    continue

                if on_delete_behavior == CASCADE:
                    related_obj.soft_delete()
                elif on_delete_behavior == SET_NULL:
                    setattr(related_obj, related_field_name, None)
                    related_obj.save(update_fields=[related_field_name])

    def soft_delete(self):
        """Soft delete and simulate on_delete behavior for related fields."""
        user = get_current_user()
        self.is_deleted = True
        self.deleted_by = user
        self.deleted_at = timezone.now()
        self.status = "inactive"
        self.save()
        self.cascade_or_nullify()

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.status = "active"
        self.save()

    def delete(self, *args, **kwargs):
        """Override delete to perform soft delete by default."""
        user = get_current_user()
        if isinstance(user, AnonymousUser) or user is None:
            user = None

        self.is_deleted = True
        self.deleted_by = user
        self.deleted_at = timezone.now()
        self.status = "inactive"
        self.save()
        self.cascade_or_nullify()

    def hard_delete(self):
        """Permanently delete the object from the database."""
        super().delete()


class APIKey(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(48)[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"
