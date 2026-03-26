from django.contrib import admin

from ..models import Guide

__all__ = ("GuideAdmin",)


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_sign_language", "order", "is_active")
    list_display_links = ("id", "name")
    list_editable = ("is_sign_language", "order", "is_active")
    list_filter = ("is_active", "is_sign_language")
    search_fields = ("name",)
    ordering = ("order",)
