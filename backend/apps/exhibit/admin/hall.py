from django.contrib import admin
from django.utils.html import format_html
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
    list_display = ("name", "order", "transition_seconds", "map_thumb", "transition_map_thumb", "is_active")
    list_filter = ("is_active",)
    list_editable = ("order", "transition_seconds", "is_active")
    search_fields = ("name",)
    inlines = [SectionInline]

    @admin.display(description="Карта зала")
    def map_thumb(self, obj):
        if obj.map_image:
            return format_html('<img src="{}" style="max-height:50px;border-radius:4px">', obj.map_image.url)
        return "—"

    @admin.display(description="Карта перехода")
    def transition_map_thumb(self, obj):
        if obj.transition_map_image:
            return format_html('<img src="{}" style="max-height:50px;border-radius:4px">', obj.transition_map_image.url)
        return "—"
