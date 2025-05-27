from rest_framework import serializers
from .models import TermsAndConditions
from core.serializers import BaseModelSerializer


class TermsAndConditionsSerializer(BaseModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = [
            'id', 'uuid', 'title', 'description',
            'created_at', 'updated_at'
        ]
