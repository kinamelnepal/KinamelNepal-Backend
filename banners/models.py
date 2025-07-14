from django.db import models

from core.models import BaseModel


class Banner(BaseModel):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Expired", "Expired"),
    ]

    DISPLAY_LOCATION_CHOICES = [
        ("homepage__header", "Homepage Header"),
        ("homepage__sidebar", "Homepage Sidebar"),
        ("homepage__footer", "Homepage Footer"),
        ("homepage__main", "Homepage Main"),
        ("homepage__section_1", "Homepage Section 1"),
        ("homepage__section_2", "Homepage Section 2"),
        ("homepage__section_3", "Homepage Section 3"),
        ("homepage__section_4", "Homepage Section 4"),
        ("homepage__section_5", "Homepage Section 5"),
        ("homepage__section_6", "Homepage Section 6"),
        ("product_page__header", "Product Page Header"),
        ("product_page__sidebar", "Product Page Sidebar"),
        ("product_page__footer", "Product Page Footer"),
        ("category_page__header", "Category Page Header"),
        ("category_page__sidebar", "Category Page Sidebar"),
        ("category_page__footer", "Category Page Footer"),
        ("popup__main", "Popup Main"),
        ("offers", "Offers"),
    ]

    title = models.CharField(max_length=255, unique=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(
        upload_to="banners/", null=True, blank=True, verbose_name="Banner Image"
    )
    call_to_action_link = models.URLField(max_length=255, blank=True, null=True)
    call_to_action_text = models.CharField(max_length=100, blank=True, null=True)
    show_call_to_action = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Active")
    display_order = models.PositiveIntegerField(default=1)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    display_location = models.CharField(
        max_length=50, choices=DISPLAY_LOCATION_CHOICES, default="homepage__header"
    )

    class Meta:
        ordering = ["display_order", "-start_date"]
        verbose_name_plural = "Banners"

    def __str__(self):
        return self.title
