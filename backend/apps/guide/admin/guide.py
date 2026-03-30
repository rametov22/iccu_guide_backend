from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from ..models import Guide, GuideVideo

__all__ = ("GuideAdmin",)


class GuideVideoInline(TranslationTabularInline):
    model = GuideVideo
    extra = 1
    ordering = ("section", "order")
    autocomplete_fields = ("section",)


@admin.register(Guide)
class GuideAdmin(TabbedTranslationAdmin):
    list_display = ("id", "name", "avatar_thumb", "is_sign_language", "order", "is_active")
    list_display_links = ("id", "name")
    list_editable = ("is_sign_language", "order", "is_active")
    list_filter = ("is_active", "is_sign_language")
    search_fields = ("name",)
    ordering = ("order",)
    inlines = [GuideVideoInline]

    @admin.display(description="Фото")
    def avatar_thumb(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height:50px;border-radius:50%">', obj.thumbnail.url)
        return "—"
