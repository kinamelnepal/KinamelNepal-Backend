from rest_framework import serializers
from .models import Faq
from core.serializers import BaseModelSerializer


class FaqSerializer(BaseModelSerializer):
    class Meta:
        model = Faq
        fields = [
            'id', 'uuid', 'question', 'answer',
            'created_at', 'updated_at'
        ]
