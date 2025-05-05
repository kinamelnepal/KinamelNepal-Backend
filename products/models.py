from django.db import models
from core.models import BaseModel

class Product(BaseModel):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Out Of Stock', 'Out Of Stock'),
        ('Disabled', 'Disabled'),
    ]
    SALE_CHOICES = [
        ('New', 'New'),
        ('Sale', 'Sale'),
        ('Featured', 'Featured'),
        ('Best Seller', 'Best Seller'),
        ('Top Rated', 'Top Rated'),
        ('Limited Edition', 'Limited Edition'),
        ('Exclusive', 'Exclusive'),
        ('Clearance', 'Clearance'),
        ('Pre-Order', 'Pre-Order'),
        ('Backorder', 'Backorder'),
        ('Seasonal', 'Seasonal'),
        ('Limited Time Offer', 'Limited Time Offer'),
        ('Bundle', 'Bundle'),
        ('Gift Set', 'Gift Set'),
        ('Subscription', 'Subscription'),
        ('Trending', 'Trending'),
        ('Best Deal', 'Best Deal'),

    ]
    LOCATION_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    ]
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE, related_name='products', verbose_name="Product Category", null=True, blank=True)  
    sale = models.CharField(max_length=50, blank=True, null=True,choices=SALE_CHOICES,default='New')
    image = models.ImageField(upload_to='products/images/', null=True, blank=True, verbose_name="Product Image")
    image_two = models.ImageField(upload_to='products/images/', null=True, blank=True, verbose_name="Product Image 2")
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    title = models.CharField(max_length=255, unique=True)
    rating = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Available')
    location = models.CharField(max_length=255,choices=LOCATION_CHOICES, default='Online')
    brand = models.CharField(max_length=255)
    sku = models.IntegerField(unique=True)
    quantity = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Weight (kg)")
    dimensions = models.CharField(max_length=255, null=True, blank=True, verbose_name="Dimensions (cm)")

    # unique_fields = ['title']

    class Meta:
        ordering = ['-created_at', 'quantity']
        verbose_name_plural = "Products"

    def __str__(self):
        return self.title
