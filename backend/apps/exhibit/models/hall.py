from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Hall",)


class Hall(models.Model):
    """
    Зал музея (верхний уровень иерархии).
    Пример: «Доисламский период».
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("Название"),
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Описание"),
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок"),
    )

    transition_seconds = models.PositiveIntegerField(
        default=60,
        verbose_name=_("Время перехода (секунд)"),
        help_text=_("Время на переход между залами"),
    )

    map_image = models.ImageField(
        upload_to="halls/maps/",
        blank=True,
        null=True,
        verbose_name=_("Карта зала"),
    )

    transition_map_image = models.ImageField(
        upload_to="halls/transition_maps/",
        blank=True,
        null=True,
        verbose_name=_("Карта перехода к залу"),
        help_text=_("Показывается туристам при переходе в этот зал"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
    )

    class Meta:
        verbose_name = _("Зал")
        verbose_name_plural = _("Залы")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name
