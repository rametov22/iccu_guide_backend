from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from ..models import Guide, GuideVideo, GuideHallVideo

__all__ = ("GuideAdmin", "GuideHallVideoAdmin")


class GuideVideoInline(TranslationTabularInline):
    model = GuideVideo
    extra = 1
    ordering = ("section", "order")
    autocomplete_fields = ("section",)


class GuideHallVideoInline(TranslationTabularInline):
    model = GuideHallVideo
    extra = 1
    autocomplete_fields = ("hall",)


@admin.register(Guide)
class GuideAdmin(TabbedTranslationAdmin):
    list_display = ("id", "name", "avatar_thumb", "is_sign_language", "order", "is_active")
    list_display_links = ("id", "name")
    list_editable = ("is_sign_language", "order", "is_active")
    list_filter = ("is_active", "is_sign_language")
    search_fields = ("name",)
    ordering = ("order",)
    inlines = [GuideVideoInline, GuideHallVideoInline]

    @admin.display(description="Фото")
    def avatar_thumb(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height:50px;border-radius:50%">', obj.thumbnail.url)
        return "—"


@admin.register(GuideHallVideo)
class GuideHallVideoAdmin(TabbedTranslationAdmin):
    list_display = ("guide", "hall", "has_video")
    list_filter = ("guide", "hall")
    autocomplete_fields = ("guide", "hall")

    @admin.display(description="Видео", boolean=True)
    def has_video(self, obj):
        return bool(obj.video)
