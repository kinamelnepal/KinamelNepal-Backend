from rest_framework import serializers
from .models import Contact
from core.serializers import BaseModelSerializer


class ContactSerializer(BaseModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id', 'uuid', 'full_name', 'email', 'phone', 'message',
            'created_at', 'updated_at'
        ]
