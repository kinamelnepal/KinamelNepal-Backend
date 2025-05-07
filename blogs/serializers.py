
from .models import Blog, BlogCategory
from core.serializers import BaseModelSerializer
from rest_framework import serializers

class BlogCategorySerializer(BaseModelSerializer):
    class Meta:
        model = BlogCategory
        fields = [
            'id', 'uuid','slug', 'name', 'description', 'image',
            'created_at', 'updated_at'
        ]

class BlogSerializer(BaseModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BlogCategory.objects.all(),
        source='category',
        write_only=True
    )
    class Meta:
        model = Blog
        fields = [
            'id', 'uuid', 'slug', 'category', 'title', 'image', 'date',
            'description', 'created_at', 'updated_at','category_id'
        ]
