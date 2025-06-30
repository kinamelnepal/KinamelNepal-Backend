from django.db import models

from core.models import BaseModel


class ReturnPolicy(BaseModel):
    title = models.CharField(max_length=500)
    description = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Return Policy"

    def __str__(self):
        return self.title
