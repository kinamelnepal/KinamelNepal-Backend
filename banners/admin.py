from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from core.admin import SoftDeleteAdmin
from core.mixins import FormatBaseModelFieldsMixin, HideBaseModelFieldsMixin

from .models import Banner


@admin.register(Banner)
class BannerAdmin(
    HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin
):
    list_display = (
        "id",
        "banner_image",
        "title",
        "subtitle",
        "status",
        "display_location",
        "display_order",
        "formatted_start_date",
        "formatted_end_date",
        "show_call_to_action",
        "is_deleted_display",
    )
    search_fields = ("title", "subtitle", "display_location")
    list_filter = (
        "status",
        "display_location",
        "show_call_to_action",
        "start_date",
        "end_date",
    )
    ordering = ("-start_date", "display_order")
    readonly_fields = ("created_at", "updated_at")

    def banner_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.image.url,
            )
        return "No Image"

    banner_image.short_description = "Image"

    def formatted_start_date(self, obj):
        return (
            obj.start_date.strftime("%Y-%m-%d %H:%M:%S")
            if obj.start_date
            else "Not Set"
        )

    formatted_start_date.short_description = "Start Date"

    def formatted_end_date(self, obj):
        return obj.end_date.strftime("%Y-%m-%d %H:%M:%S") if obj.end_date else "Not Set"

    formatted_end_date.short_description = "End Date"

    def is_deleted_display(self, obj):
        return "Yes" if obj.is_deleted else "No"

    is_deleted_display.short_description = "Is Deleted"

    def show_call_to_action(self, obj):
        return "Yes" if obj.show_call_to_action else "No"

    show_call_to_action.short_description = "Show Call To Action"
