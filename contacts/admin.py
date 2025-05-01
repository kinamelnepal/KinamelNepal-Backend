from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Contact
from core.mixins import HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin
from core.admin import SoftDeleteAdmin


@admin.register(Contact)
class ContactAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'short_message', 'formatted_created_at', 'is_deleted_display')
    search_fields = ('full_name', 'email', 'phone')
    list_filter = ('created_at',)
    ordering = ('-created_at', 'full_name')

    def short_message(self, obj):
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message'
