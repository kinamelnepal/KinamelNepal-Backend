# managers.py
from django.db import models
from django.utils import timezone

class BaseModelManager(models.Manager):
    def get_queryset(self):

        return super().get_queryset().filter(is_deleted=False) 

    def deleted(self):
        """Include soft-deleted items in the queryset."""
        return super().get_queryset().filter(is_deleted=True)

    def active(self):
        """Retrieve active items (status='active')."""
        return super().get_queryset().filter(status='active')
