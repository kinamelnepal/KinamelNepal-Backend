from django.db import models

from core.models import BaseModel


class Contact(BaseModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.full_name} - {self.email}"
