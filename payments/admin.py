from django import forms

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from core.admin import SoftDeleteAdmin
from core.mixins import FormatBaseModelFieldsMixin, HideBaseModelFieldsMixin

from .models import Payment


# Custom form for Payment model
class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = "__all__"


@admin.register(Payment)
class PaymentAdmin(
    HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin
):
    form = PaymentAdminForm
    list_display = (
        "id",
        "order_link",
        "method",
        "payment_status",
        "amount_display",
        "tax_amount_display",
        "total_amount_display",
        "transaction_id",
        "paid_at_formatted",
        "is_deleted_display",
    )
    search_fields = (
        "order__id",
        "transaction_id",
        "method",
        "payment_status",
        "card_last4",
        "card_brand",
        "product_code",
        "notes",
    )
    list_filter = (
        "method",
        "payment_status",
        "paid_at",
    )
    ordering = ("-created_at", "payment_status")
    readonly_fields = ("created_at", "updated_at", "paid_at")

    def order_link(self, obj):
        if obj.order:
            return format_html(
                '<a href="/admin/orders/order/{}/change/">{}</a>',
                obj.order.id,
                f"Order #{obj.order.id}",
            )
        return "-"

    order_link.short_description = "Order"

    def amount_display(self, obj):
        return f"Rs {obj.amount:.2f}"

    amount_display.short_description = "Amount"

    def tax_amount_display(self, obj):
        return f"Rs {obj.tax_amount:.2f}"

    tax_amount_display.short_description = "Tax Amount"

    def total_amount_display(self, obj):
        return f"Rs {obj.total_amount:.2f}"

    total_amount_display.short_description = "Total Amount"

    def paid_at_formatted(self, obj):
        if obj.paid_at:
            return obj.paid_at.strftime("%Y-%m-%d %H:%M:%S")
        return "-"

    paid_at_formatted.short_description = "Paid At"
