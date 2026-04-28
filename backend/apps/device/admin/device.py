from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html

from ..models import Device, DeviceFileState
from ..services import send_push_to_tokens

__all__ = ("DeviceAdmin", "DeviceFileStateAdmin")


class DeviceFileStateInline(admin.TabularInline):
    model = DeviceFileState
    extra = 0
    can_delete = False
    fields = ("file_url", "status", "progress", "file_size", "updated_at")
    readonly_fields = ("file_url", "status", "progress", "file_size", "updated_at")
    show_change_link = False


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "name_or_token", "is_active", "files_summary",
                    "last_seen_at", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "fcm_token")
    readonly_fields = ("fcm_token", "last_seen_at", "created_at")
    actions = ("send_test_push",)
    inlines = [DeviceFileStateInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _total=Count("file_states"),
            _done=Count("file_states", filter=Q(file_states__status=DeviceFileState.Status.DONE)),
            _err=Count("file_states", filter=Q(file_states__status=DeviceFileState.Status.ERROR)),
        )

    def name_or_token(self, obj):
        return obj.name or obj.fcm_token[:12]
    name_or_token.short_description = "Имя"

    def files_summary(self, obj):
        total = getattr(obj, "_total", 0)
        done = getattr(obj, "_done", 0)
        err = getattr(obj, "_err", 0)
        color = "#16a34a" if done == total and total > 0 else "#a16207"
        if err:
            color = "#b91c1c"
        return format_html(
            '<span style="color:{}">{}/{}</span>{}',
            color, done, total,
            f" · {err} ошибок" if err else "",
        )
    files_summary.short_description = "Скачано"

    @admin.action(description="Отправить тестовый push")
    def send_test_push(self, request, queryset):
        tokens = list(queryset.values_list("fcm_token", flat=True))
        result = send_push_to_tokens(
            tokens,
            title="Тест",
            body="Это тестовое уведомление",
            data={"action": "test"},
        )
        ok = result.get("success_count", 0) if result else 0
        fail = result.get("failure_count", 0) if result else 0
        self.message_user(
            request,
            f"Отправлено: {ok} из {len(tokens)}, ошибок: {fail}",
        )


@admin.register(DeviceFileState)
class DeviceFileStateAdmin(admin.ModelAdmin):
    list_display = ("device", "file_url_short", "status", "progress",
                    "file_size", "updated_at")
    list_filter = ("status",)
    search_fields = ("file_url", "device__name", "device__fcm_token")
    readonly_fields = ("device", "file_url", "updated_at", "created_at")

    def file_url_short(self, obj):
        url = obj.file_url
        return url if len(url) <= 60 else f"…{url[-58:]}"
    file_url_short.short_description = "URL"
