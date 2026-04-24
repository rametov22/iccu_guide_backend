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


class GuideVideoInline(admin.TabularInline):
    from guide.models import GuideVideo
    model = GuideVideo
    extra = 0
    fields = ("guide", "order", "duration_display", "video_link")
    readonly_fields = ("duration_display", "video_link")
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Длительность")
    def duration_display(self, obj):
        if not obj.duration_seconds:
            return "—"
        m, s = divmod(obj.duration_seconds, 60)
        return f"{m}:{s:02d}"

    @admin.display(description="Видео")
    def video_link(self, obj):
        if obj.video:
            return format_html('<a href="{}" target="_blank">&#9654;</a>', obj.video.url)
        return "—"


@admin.register(Section)
class SectionAdmin(TabbedTranslationAdmin):
    list_display = ("name", "hall", "order", "effective_duration_display", "break_duration_seconds", "transition_seconds", "map_thumb", "video_preview", "is_active")
    list_filter = ("is_active", "hall")
    list_editable = ("order", "break_duration_seconds", "transition_seconds", "is_active")
    search_fields = ("name",)
    readonly_fields = ("duration_from_guide_videos",)
    inlines = [ExhibitInline, GuideVideoInline]

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj and obj.pk and obj.guide_videos.exists():
            # Если есть видео гидов — duration_seconds берётся из них, скрываем ручное поле
            # и показываем readonly-отображение
            if "duration_seconds" in fields:
                fields.remove("duration_seconds")
        else:
            # Нет видео гидов — убираем readonly-отображение, оставляем ручное поле
            if "duration_from_guide_videos" in fields:
                fields.remove("duration_from_guide_videos")
        return fields

    @admin.display(description="Длительность (из видео гида)")
    def duration_from_guide_videos(self, obj):
        secs = obj.effective_duration_seconds
        m, s = divmod(secs, 60)
        return format_html(
            "<b>{}:{:02d}</b> — max видео гида + 1 сек. Менять нельзя, задаётся автоматически.",
            m, s,
        )

    @admin.display(description="Длительность", ordering="duration_seconds")
    def effective_duration_display(self, obj):
        secs = obj.effective_duration_seconds
        m, s = divmod(secs, 60)
        has_gv = obj.guide_videos.exists()
        label = "из видео" if has_gv else "вручную"
        return format_html("{}:{:02d} <small>({})</small>", m, s, label)

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
