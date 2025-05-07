from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Blog, BlogCategory
from core.mixins import HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin
from core.admin import SoftDeleteAdmin

@admin.register(Blog)
class BlogAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = ('id', 'blog_image', 'title', 'category', 'date', 'formatted_created_at', 'is_deleted_display')
    search_fields = ('title', 'category__name')
    list_filter = ('category', 'date')
    ordering = ('-date', 'category')

    def blog_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return "No Image"
    blog_image.short_description = 'Image'

@admin.register(BlogCategory)
class BlogCategoryAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = ('id', 'category_image', 'name', 'formatted_created_at', 'is_deleted_display')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def category_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return "No Image"
    category_image.short_description = 'Category Image'
