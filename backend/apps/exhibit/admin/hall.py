from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from ..models import Hall, Section

__all__ = ("HallAdmin",)


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ("name", "order", "is_active")
    show_change_link = True


@admin.register(Hall)
class HallAdmin(TabbedTranslationAdmin):
    list_display = ("name", "order", "is_active")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("name",)
    inlines = [SectionInline]
