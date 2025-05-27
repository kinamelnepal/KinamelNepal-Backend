from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ReturnPolicy
from core.mixins import HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin
from core.admin import SoftDeleteAdmin


@admin.register(ReturnPolicy)
class ReturnPolicyAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = ('id', 'title', 'short_description', 'formatted_created_at', 'is_deleted_display')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at', 'title')

    def short_description(self, obj):
        return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description
    short_description.short_description = 'Description'
