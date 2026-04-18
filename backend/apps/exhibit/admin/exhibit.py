from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from ..models import Exhibit, ExhibitImage

__all__ = ("ExhibitAdmin",)


class ExhibitImageInline(admin.TabularInline):
    model = ExhibitImage
    extra = 1
    fields = ("image", "order", "preview")
    readonly_fields = ("preview",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:60px;border-radius:4px">', obj.image.url)
        return "—"


@admin.register(Exhibit)
class ExhibitAdmin(TabbedTranslationAdmin):
    list_display = ("title", "section", "order", "thumb", "is_active")
    list_filter = ("is_active", "section__hall")
    list_editable = ("order", "is_active")
    search_fields = ("title",)
    inlines = [ExhibitImageInline]

    @admin.display(description="Фото")
    def thumb(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height:50px;border-radius:4px">', obj.thumbnail.url)
        return "—"
