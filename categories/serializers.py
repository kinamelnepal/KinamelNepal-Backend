from rest_framework import serializers
from .models import Category
from core.serializers import BaseModelSerializer

class CategorySerializer(BaseModelSerializer):
    products_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Category
        fields = [
            'id', 'uuid', 'slug', 'name', 'persantine', 'icon', 'image', 'item', 'num',
            'created_at', 'updated_at','products_count'
        ]
    def get_products_count(self,obj):
        """
        Returns the count of products in the queryset.
        """
        return obj.products.count()