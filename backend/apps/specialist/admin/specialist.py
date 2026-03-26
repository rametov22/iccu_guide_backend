from django.contrib import admin

from ..models import Specialist

__all__ = ("SpecialistAdmin",)


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "is_active")
    list_display_links = ("number",)
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "number")
    ordering = ("number",)

    def name(self, obj):
        return obj.name

    name.short_description = "Имя"
