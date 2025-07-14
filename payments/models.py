from django.db import models

from core.models import BaseModel


class Payment(BaseModel):
    PAYMENT_METHOD_CHOICES = [
        ("COD", "Cash On Delivery"),
        ("Card", "Card"),
        ("Esewa", "Esewa"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="payment"
    )
    method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cod"
    )
    payment_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    # For eSewa-specific fields
    product_code = models.CharField(max_length=100, blank=True, null=True)
    signed_field_names = models.CharField(max_length=255, blank=True, null=True)
    signature = models.CharField(max_length=255, blank=True, null=True)

    # Card-specific metadata
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=50, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.method} - {self.payment_status}"
