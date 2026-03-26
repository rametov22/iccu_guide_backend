from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

__all__ = ("Specialist",)


class Specialist(models.Model):
    """
    Профиль специалиста (гида).
    OneToOne к User — специалист логинится через username/password,
    а номер на бейдже и аватар хранятся здесь.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="specialist_profile",
        verbose_name=_("Пользователь"),
    )

    number = models.PositiveIntegerField(
        unique=True,
        verbose_name=_("Номер"),
        help_text=_("Уникальный номер на бейдже"),
    )

    avatar = models.ImageField(
        upload_to="specialists/avatars/",
        blank=True,
        null=True,
        verbose_name=_("Аватар"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
    )

    class Meta:
        verbose_name = _("Специалист")
        verbose_name_plural = _("Специалисты")
        ordering = ["number"]

    def __str__(self):
        return f"#{self.number} — {self.name}"

    @property
    def name(self):
        return self.user.get_full_name() or self.user.username
