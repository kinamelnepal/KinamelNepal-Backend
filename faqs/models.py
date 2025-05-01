from django.db import models
from core.models import BaseModel


class Faq(BaseModel):
    question = models.CharField(max_length=500)
    answer = models.TextField()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
