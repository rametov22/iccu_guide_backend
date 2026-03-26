from django.contrib import admin

from ..models import Background

__all__ = ("BackgroundAdmin",)


@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    ordering = ("order",)
