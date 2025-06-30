from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Address(BaseModel):
    ADDRESS_TYPE_CHOICES = [
        ("Shipping", "Shipping"),
        ("Billing", "Billing"),
        ("Both", "Both"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    address_type = models.CharField(
        max_length=20, choices=ADDRESS_TYPE_CHOICES, default="Shipping"
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.address_type} - {self.city}"
