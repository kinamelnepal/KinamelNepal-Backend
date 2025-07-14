from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from core.admin import SoftDeleteAdmin
from core.mixins import FormatBaseModelFieldsMixin, HideBaseModelFieldsMixin

from .models import Product


# Custom form for rich text support
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "description": CKEditorWidget(),
            "short_description": CKEditorWidget(),
        }


@admin.register(Product)
class ProductAdmin(
    HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin
):
    form = ProductAdminForm  # <-- Inject the custom form here
    list_display = (
        "id",
        "product_image",
        "title",
        "category",
        "new_price",
        "old_price",
        "status",
        "brand",
        "sku",
        "formatted_created_at",
        "is_deleted_display",
    )
    search_fields = ("title", "category__name", "brand")
    list_filter = (
        "status",
        "category",
        "brand",
        "sale",
        "location",
        "rating",
        "sku",
        "new_price",
        "old_price",
    )
    ordering = ("-created_at", "category", "brand")
    readonly_fields = ("created_at", "updated_at")

    def product_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.image.url,
            )
        return "No Image"

    product_image.short_description = "Image"

    def product_image_two(self, obj):
        if obj.image_two:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.image_two.url,
            )
        return "No Image"

    product_image_two.short_description = "Second Image"
