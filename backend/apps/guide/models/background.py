from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Background",)


class Background(models.Model):
    """Фоновое изображение для фронтенда."""

    image = models.ImageField(
        upload_to="backgrounds/",
        verbose_name=_("Изображение"),
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
    )

    class Meta:
        verbose_name = _("Фон")
        verbose_name_plural = _("Фоны")
        ordering = ["order"]

    def __str__(self):
        return f"Background #{self.pk}"
