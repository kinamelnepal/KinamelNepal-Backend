from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Category
from core.mixins import HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin
from core.admin import SoftDeleteAdmin

@admin.register(Category)
class CategoryAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = ('id', 'name', 'persantine', 'item', 'num', 'category_image', 'formatted_created_at', 'is_deleted_display')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('item', 'num', 'name', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def category_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return "No Image"
    category_image.short_description = 'Image'
