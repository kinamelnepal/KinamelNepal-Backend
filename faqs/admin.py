from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Faq
from core.mixins import HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin
from core.admin import SoftDeleteAdmin


@admin.register(Faq)
class FaqAdmin(HideBaseModelFieldsMixin, FormatBaseModelFieldsMixin, SoftDeleteAdmin, ModelAdmin):
    list_display = ('id', 'question', 'short_answer', 'formatted_created_at', 'is_deleted_display')
    search_fields = ('question', 'answer')
    list_filter = ('created_at',)
    ordering = ('-created_at', 'question')

    def short_answer(self, obj):
        return (obj.answer[:50] + '...') if len(obj.answer) > 50 else obj.answer
    short_answer.short_description = 'Answer'
