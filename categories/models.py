from django.db import models
from django.utils.text import slugify

from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    persantine = models.CharField(max_length=10, blank=True)
    icon = models.CharField(max_length=255, blank=True)
    image = models.ImageField(
        upload_to="categories/images/",
        null=True,
        blank=True,
        verbose_name="Category Image",
    )  # Use ImageField for local or other image storage
    item = models.PositiveIntegerField(default=0)
    num = models.PositiveIntegerField(default=0)

    unique_fields = ["name"]

    class Meta:
        ordering = ["num", "name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
