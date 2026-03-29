from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Section",)


class Section(models.Model):
    """
    Раздел внутри зала (второй уровень иерархии).
    Пример: «Бактрийская цивилизация» внутри зала «Доисламский период».
    """

    hall = models.ForeignKey(
        "exhibit.Hall",
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("Зал"),
    )

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

    duration_seconds = models.PositiveIntegerField(
        default=600,
        verbose_name=_("Длительность (секунд)"),
    )

    break_duration_seconds = models.PositiveIntegerField(
        default=300,
        verbose_name=_("Перерыв после раздела (секунд)"),
        help_text=_("Длительность перерыва после завершения этого раздела"),
    )

    video = models.FileField(
        upload_to="sections/videos/",
        blank=True,
        null=True,
        verbose_name=_("Видео раздела"),
    )

    map_image = models.ImageField(
        upload_to="sections/maps/",
        blank=True,
        null=True,
        verbose_name=_("Карта раздела"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
    )

    class Meta:
        verbose_name = _("Раздел")
        verbose_name_plural = _("Разделы")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.hall.name} → {self.name}"
