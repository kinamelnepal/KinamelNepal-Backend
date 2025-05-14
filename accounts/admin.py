from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Address
from core.mixins import HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin
from core.admin import SoftDeleteAdmin


@admin.register(Address)
class AddressAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = (
        'id', 'full_name', 'phone_number', 'city', 'country',
        'address_type', 'is_default', 'formatted_created_at', 'is_deleted_display'
    )
    search_fields = ('full_name', 'phone_number', 'email', 'city', 'state', 'postal_code')
    list_filter = ('country', 'address_type', 'is_default', 'created_at')
    ordering = ('-created_at', 'full_name')
