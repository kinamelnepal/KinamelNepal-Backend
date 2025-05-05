from rest_framework import serializers
from .models import Product
from core.serializers import BaseModelSerializer

class ProductSerializer(BaseModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'uuid', 'category', 'sale', 'image', 'image_two', 'new_price', 'old_price','weight','quantity',
            'description', 'dimensions','title', 'rating', 'status', 'location', 'brand', 'sku', 'created_at', 'updated_at'
        ]

