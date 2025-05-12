from rest_framework import serializers
from .models import Product
from core.serializers import BaseModelSerializer
from categories.serializers import CategorySerializer

class ProductSerializer(BaseModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    products_count = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id', 'uuid', 'category', 'sale', 'image', 'image_two', 'new_price', 'old_price','weight','quantity',
            'description', 'dimensions','title', 'rating', 'status', 'location', 'brand', 'sku', 'created_at', 'updated_at'
        ]

   