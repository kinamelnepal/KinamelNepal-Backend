
from django.contrib import admin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html

# Register the default Django Group model with the django-unfold GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, ModelAdmin)

class SoftDeleteAdmin(admin.ModelAdmin):

    # Display only non-deleted objects in the list view by default
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.GET.get('show_deleted', None):
            return queryset.filter(is_deleted=False)
        return queryset

    # Customize the list display to show a visual indicator for soft-deleted records
    def is_deleted_display(self, obj):
        if obj.is_deleted :
            return format_html('<span style="color: red; font-weight: bold;">Soft Deleted</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_deleted_display.short_description = 'Status'

    def soft_delete_selected(self, request, queryset):
        """Soft delete selected objects."""
        updated_count = queryset.update(is_deleted=True, status='inactive', deleted_at=timezone.now(), deleted_by=request.user)
        self.message_user(request, f"{updated_count} item(s) marked as deleted.")
    soft_delete_selected.short_description = "Soft delete selected items"

    # Adding action to restore soft-deleted records
    def restore_selected(self, request, queryset):
        # Ensure only soft-deleted records are restored
        restored_count = queryset.filter(is_deleted=True).update(is_deleted=False, deleted_at=None)
        self.message_user(request, f'{restored_count} record(s) restored successfully!')
    restore_selected.short_description = "Restore selected records"

    # Adding action to permanently delete soft-deleted records
    def hard_delete_selected(self, request, queryset):
        # Delete records permanently (no restore option)
        deleted_count, _ = queryset.filter(is_deleted=True).delete()
        self.message_user(request, f'{deleted_count} soft-deleted record(s) permanently deleted!')
    hard_delete_selected.short_description = "Permanently delete selected soft-deleted records"

    # Custom actions for soft delete and restore
    actions = ['restore_selected', 'hard_delete_selected','soft_delete_selected']



