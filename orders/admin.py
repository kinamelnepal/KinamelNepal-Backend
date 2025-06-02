from django.contrib import admin
from django import forms
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from core.mixins import HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin
from core.admin import SoftDeleteAdmin
from .models import Order, OrderItem
from accounts.models import Address

# Custom form for Order model
class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

@admin.register(Order)
class OrderAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    form = OrderAdminForm  # Custom form for the Order model
    list_display = (
        'id', 'full_name', 'email', 'phone_number', 'order_status', 'payment_status', "is_completed",
        'payment_method', 'total', 'formatted_created_at', 'formatted_updated_at', 'is_deleted_display'
    )
    search_fields = ('full_name', 'email', 'phone_number', 'order_status', 'payment_method')
    list_filter = ('order_status', 'payment_method', 'payment_status', 'shipping_address', 'billing_address')
    ordering = ('-created_at', 'order_status')
    readonly_fields = ('created_at', 'updated_at')

    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    formatted_created_at.short_description = 'Created At'

    def formatted_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    formatted_updated_at.short_description = 'Updated At'

    def shipping_address_display(self, obj):
        if obj.shipping_address:
            return format_html('<span>{}</span>', obj.shipping_address)
        return "No Address"
    shipping_address_display.short_description = 'Shipping Address'

    def billing_address_display(self, obj):
        if obj.billing_address:
            return format_html('<span>{}</span>', obj.billing_address)
        return "No Address"
    billing_address_display.short_description = 'Billing Address'


# Custom form for OrderItem model
class OrderItemAdminForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'

@admin.register(OrderItem)
class OrderItemAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = (
        'id', 'order', 'product', 'quantity', 'price', 'discount', 'total', 
        'formatted_created_at', 'formatted_updated_at', 'total_display', 'product_image'
    )
    search_fields = ('order__id', 'product__title', 'quantity')
    list_filter = ('order', 'product', 'quantity', 'price', 'discount')
    ordering = ('-created_at', 'product__title')
    readonly_fields = ('created_at', 'updated_at')

    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    formatted_created_at.short_description = 'Created At'

    def formatted_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    formatted_updated_at.short_description = 'Updated At'

    def total_display(self, obj):
        return f"Rs {obj.total:.2f}"
    total_display.short_description = 'Total'

    def product_image(self, obj):
        if obj.product.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.product.image.url)
        return "No Image"
    product_image.short_description = 'Product Image'

