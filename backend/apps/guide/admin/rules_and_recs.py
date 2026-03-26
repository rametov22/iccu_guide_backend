from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from ..models import Rule

__all__ = ("RuleAdmin",)


@admin.register(Rule)
class RuleAdmin(TabbedTranslationAdmin):
    list_display = ("number", "title", "is_active")
    list_display_links = ("number", "title")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    ordering = ("number",)
    search_fields = ("title",)

    class Media:
        css = {"all": ("admin/css/martor_fix.css",)}
