from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from ..models import Section, Exhibit

__all__ = ("SectionAdmin",)


class ExhibitInline(admin.TabularInline):
    model = Exhibit
    extra = 0
    fields = ("title", "order", "is_active")
    show_change_link = True


@admin.register(Section)
class SectionAdmin(TabbedTranslationAdmin):
    list_display = ("name", "hall", "order", "duration_minutes", "break_duration_minutes", "is_active")
    list_filter = ("is_active", "hall")
    list_editable = ("order", "duration_minutes", "break_duration_minutes", "is_active")
    search_fields = ("name",)
    inlines = [ExhibitInline]
