from rest_framework import serializers
from .models import Category
from core.serializers import BaseModelSerializer

class CategorySerializer(BaseModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'uuid', 'slug', 'name', 'persantine', 'icon', 'image', 'item', 'num',
            'created_at', 'updated_at'
        ]
