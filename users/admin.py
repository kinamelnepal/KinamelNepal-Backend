# users/admin.py
from hashlib import md5

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from core.admin import SoftDeleteAdmin
from core.mixins import FormatBaseModelFieldsMixin, HideBaseModelFieldsMixin

from .models import User


@admin.register(User)
class UserAdmin(
    HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin
):
    list_display = (
        "id",
        "avatar_image",
        "full_name",
        "email",
        "role",
        "formatted_created_at",
        "is_deleted_display",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
    )
    readonly_fields = ("password", "last_login", "groups", "updated_at", "created_at")
    list_filter = ("role", "created_at")
    ordering = ("-created_at",)

    def avatar_image(self, obj):
        if obj.avatar:  # Use the uploaded avatar if it exists
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.avatar.url,
            )

        email_hash = md5(obj.email.lower().encode("utf-8")).hexdigest()
        gravatar_url = (
            f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=50&f=y"
        )

        return format_html(
            '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
            gravatar_url,
        )

    def full_name(self, obj):
        return (
            f"{obj.first_name} {obj.last_name}"
            if obj.first_name and obj.last_name
            else "N/A"
        )

    full_name.short_description = "Full Name"
