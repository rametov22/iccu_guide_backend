from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from ..models import Exhibit

__all__ = ("ExhibitAdmin",)


@admin.register(Exhibit)
class ExhibitAdmin(TabbedTranslationAdmin):
    list_display = ("title", "section", "order", "is_active")
    list_filter = ("is_active", "section__hall")
    list_editable = ("order", "is_active")
    search_fields = ("title",)
