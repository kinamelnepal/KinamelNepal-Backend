from django.db import models
from core.models import BaseModel

class Blog(BaseModel):
    category = models.ForeignKey(
        'blogs.BlogCategory',
        on_delete=models.CASCADE,
        related_name='blogs',
        verbose_name="Blog Category",
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to='blogs/images/',
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Blog Image"
    )
    date = models.DateField(
        verbose_name="Published Date"
    )
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Blog Title"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Short Description"
    )

    class Meta:
        verbose_name_plural = "Blogs"

    def __str__(self):
        return self.title


class BlogCategory(BaseModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Category Name"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Category Description"
    )
    image = models.ImageField(
        upload_to='blogs/categories/',
        null=True,
        blank=True,
        verbose_name="Category Image"
    )
    class Meta:
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name
