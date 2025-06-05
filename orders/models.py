from django.db import models
from core.models import BaseModel
from django.contrib.auth import get_user_model

from products.models import Product

User = get_user_model()

class Order(BaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Processing', 'Processing'),
        ('Quality Check', 'Quality Check'),
        ('Product Dispatched', 'Product Dispatched'),
        ('Delivered', 'Delivered'),
        ('Shipped', 'Shipped'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash On Delivery'),
        ('Card', 'Card'),
        ('Esewa', 'Esewa'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    full_name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    shipping_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True, related_name='shipping_orders')
    billing_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_orders')

    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_shipped = models.BooleanField(default=False)
    shipped_at = models.DateTimeField(blank=True, null=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True, editable=False)
    delivery_estimate = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    cart = models.ForeignKey('carts.Cart', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    ordered_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        if self.order_status == "Delivered":
            self.is_completed = True
        return super().save(*args, **kwargs)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity} x {self.product.title} (Order #{self.order.id})"

    def save(self, *args, **kwargs):
        # Calculate total for each order item (price * quantity - discount)
        self.total = (self.price * self.quantity) - self.discount
        super().save(*args, **kwargs)

    def get_product_details(self):
        """
        Utility function to return the product details for this order item
        """
        return {
            "product_id": self.product.id,
            "product_name": self.product.title,
            "quantity": self.quantity,
            "price": str(self.price),
            "discount": str(self.discount),
            "total": str(self.total),
        }

