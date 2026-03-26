from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Exhibit",)


class Exhibit(models.Model):
    """
    Экспонат, привязанный к разделу.
    Содержит видео с объяснением гида.
    """

    section = models.ForeignKey(
        "exhibit.Section",
        on_delete=models.CASCADE,
        related_name="exhibits",
        verbose_name=_("Раздел"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Название"),
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Описание"),
    )

    video = models.FileField(
        upload_to="exhibits/videos/",
        blank=True,
        null=True,
        verbose_name=_("Видео"),
        help_text=_("Видео экспонатов"),
    )

    thumbnail = models.ImageField(
        upload_to="exhibits/thumbnails/",
        blank=True,
        null=True,
        verbose_name=_("Превью"),
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
        verbose_name = _("Экспонат")
        verbose_name_plural = _("Экспонаты")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title
