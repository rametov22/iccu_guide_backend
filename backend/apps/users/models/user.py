from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .manager import UserManager

__all__ = ("User",)


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Специалист логинится по username + password.
    """

    class Role(models.TextChoices):
        SPECIALIST = "specialist", _("Специалист")
        ADMIN = "admin", _("Администратор")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SPECIALIST,
        verbose_name=_("Роль"),
    )

    objects = UserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_specialist(self):
        return self.role == self.Role.SPECIALIST
