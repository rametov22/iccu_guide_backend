from django.contrib import admin
from django.utils.html import format_html
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
    list_display = ("name", "hall", "order", "duration_seconds", "break_duration_seconds", "transition_seconds", "map_thumb", "video_preview", "is_active")
    list_filter = ("is_active", "hall")
    list_editable = ("order", "duration_seconds", "break_duration_seconds", "transition_seconds", "is_active")
    search_fields = ("name",)
    inlines = [ExhibitInline]

    @admin.display(description="Карта")
    def map_thumb(self, obj):
        if obj.map_image:
            return format_html('<img src="{}" style="max-height:50px;border-radius:4px">', obj.map_image.url)
        return "—"

    @admin.display(description="Видео")
    def video_preview(self, obj):
        if obj.video:
            return format_html('<a href="{}" target="_blank">&#9654; Видео</a>', obj.video.url)
        return "—"
