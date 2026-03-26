from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from specialist.models import Specialist

from ..models import User

__all__ = ("UserAdmin",)


class SpecialistInline(admin.StackedInline):
    """
    Профиль специалиста прямо на странице User.
    Создаёшь User → тут же заполняешь номер и аватар.
    """

    model = Specialist
    can_delete = False
    verbose_name = "Профиль специалиста"
    verbose_name_plural = "Профиль специалиста"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "get_full_name", "role", "is_active")
    list_filter = ("role", "is_active")
    inlines = []

    def get_inlines(self, request, obj=None):
        """Показывать инлайн специалиста только для роли specialist."""
        if obj and obj.role == User.Role.SPECIALIST:
            return [SpecialistInline]
        return []

    fieldsets = BaseUserAdmin.fieldsets + (("Роль", {"fields": ("role",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Роль", {"fields": ("role",)}),)
