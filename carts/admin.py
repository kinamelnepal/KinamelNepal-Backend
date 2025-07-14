# Register your models here.
from django.contrib import admin
from unfold.admin import ModelAdmin

from core.admin import SoftDeleteAdmin
from core.mixins import FormatBaseModelFieldsMixin, HideBaseModelFieldsMixin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(
    HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin
):
    list_display = (
        "id",
        "user_display",
        "session_key",
        "total_items_display",
        "total_price_display",
        "formatted_created_at",
        "is_deleted_display",
    )
    search_fields = ("user__email", "session_key")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")

    def user_display(self, obj):
        return obj.user.email if obj.user else "Guest"

    user_display.short_description = "User"

    def total_items_display(self, obj):
        return obj.total_items()

    total_items_display.short_description = "Total Items"

    def total_price_display(self, obj):
        return f"Rs. {obj.total_price():,.2f}"

    total_price_display.short_description = "Total Price"


@admin.register(CartItem)
class CartItemAdmin(
    HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin
):
    list_display = (
        "id",
        "product_display",
        "cart_display",
        "quantity",
        "subtotal_display",
        "formatted_created_at",
        "is_deleted_display",
    )
    search_fields = ("product__title", "cart__user__email", "cart__session_key")
    list_filter = ("product", "cart")
    readonly_fields = ("created_at", "updated_at")

    def product_display(self, obj):
        return obj.product.title

    product_display.short_description = "Product"

    def cart_display(self, obj):
        return (
            obj.cart.user.email if obj.cart.user else f"Guest ({obj.cart.session_key})"
        )

    cart_display.short_description = "Cart (User or Guest)"

    def subtotal_display(self, obj):
        return f"Rs. {obj.subtotal():,.2f}"

    subtotal_display.short_description = "Subtotal"
