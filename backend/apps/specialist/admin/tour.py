from django.contrib import admin

from ..models import TourSession

__all__ = ("TourSessionAdmin",)


@admin.register(TourSession)
class TourSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "specialist", "status", "current_section", "tourist_count", "created_at")
    list_filter = ("status", "specialist")
    readonly_fields = ("created_at", "started_at", "finished_at")
    raw_id_fields = ("current_section",)
    ordering = ("-created_at",)
